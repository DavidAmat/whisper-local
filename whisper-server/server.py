import os
import tempfile
from typing import List, Optional

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from faster_whisper import WhisperModel

# Streaming
import json
import tempfile
from starlette.responses import StreamingResponse
from fastapi import UploadFile, File, HTTPException

APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = int(os.getenv("APP_PORT", "8765"))

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "large-v3")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")  # "cuda" on your 4090
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "float16")  # best default for 4090
WHISPER_DOWNLOAD_ROOT = os.getenv("WHISPER_DOWNLOAD_ROOT", "/mnt/ssd2/whisper")

# Optional knobs
DEFAULT_BEAM_SIZE = int(os.getenv("WHISPER_BEAM_SIZE", "5"))
DEFAULT_WORD_TIMESTAMPS = os.getenv("WHISPER_WORD_TIMESTAMPS", "false").lower() == "true"

app = FastAPI(title="Whisper STT Server", version="1.0")

# Streamlit runs in browser, so allow cross-origin requests.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to ["http://localhost:8501"] if you want
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

model: Optional[WhisperModel] = None


@app.on_event("startup")
def _load_model() -> None:
    global model
    # Model is loaded once at startup (kept in GPU memory).
    model = WhisperModel(
        WHISPER_MODEL,
        device=WHISPER_DEVICE,
        compute_type=WHISPER_COMPUTE_TYPE,
        download_root=WHISPER_DOWNLOAD_ROOT,
    )


def _fmt_ts(seconds: float) -> str:
    # mm:ss.mmm
    m = int(seconds // 60)
    s = seconds - (m * 60)
    return f"{m:02d}:{s:06.3f}"


@app.get("/health")
def health():
    return {
        "ok": True,
        "model": WHISPER_MODEL,
        "device": WHISPER_DEVICE,
        "compute_type": WHISPER_COMPUTE_TYPE,
        "download_root": WHISPER_DOWNLOAD_ROOT,
    }


@app.post("/transcribe")
def transcribe(
    file: UploadFile = File(...),
    timestamps: bool = True,
    word_timestamps: bool = DEFAULT_WORD_TIMESTAMPS,
    beam_size: int = DEFAULT_BEAM_SIZE,
    language: Optional[str] = None,
):
    """
    Upload an audio file (e.g., .aac) and get back:
      - full text
      - segments with start/end timestamps
      - derived 'plain_text' and 'timestamped_text' formats for easy copying
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = os.path.splitext(file.filename)[1] or ".audio"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(file.file.read())

        segments, info = model.transcribe(
            tmp_path,
            beam_size=beam_size,
            language=language,
            word_timestamps=word_timestamps,
            vad_filter=True,
        )

        seg_list = []
        plain_parts: List[str] = []
        ts_parts: List[str] = []

        for i, seg in enumerate(segments):
            seg_text = (seg.text or "").strip()
            plain_parts.append(seg_text)

            seg_obj = {
                "id": i,
                "start": float(seg.start),
                "end": float(seg.end),
                "text": seg_text,
            }

            if word_timestamps and getattr(seg, "words", None):
                seg_obj["words"] = [
                    {
                        "start": float(w.start),
                        "end": float(w.end),
                        "word": w.word,
                        "probability": float(w.probability) if w.probability is not None else None,
                    }
                    for w in seg.words
                ]

            seg_list.append(seg_obj)

            if timestamps:
                ts_parts.append(f"[{_fmt_ts(seg.start)} → {_fmt_ts(seg.end)}] {seg_text}")
            else:
                ts_parts.append(seg_text)

        plain_text = "\n".join([p for p in plain_parts if p]).strip()
        timestamped_text = "\n".join([p for p in ts_parts if p]).strip()

        return {
            "filename": file.filename,
            "language": getattr(info, "language", None),
            "language_probability": getattr(info, "language_probability", None),
            "duration": getattr(info, "duration", None),
            "text": plain_text,
            "timestamped_text": timestamped_text,
            "segments": seg_list,
        }

    finally:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass


@app.post("/translate_stream")
def translate_stream(
    file: UploadFile = File(...),
    language: str = None,
    beam_size: int = DEFAULT_BEAM_SIZE,
):
    """
    Stream translated (to English) Whisper segments as Server-Sent Events (SSE).

    - language: REQUIRED (source language of the audio)
    - task: translate (Whisper built-in translation → English)
    - Output: incremental segment events + [DONE]
    """
    if model is None:
        raise HTTPException(status_code=500, detail="Model not loaded")

    if not language:
        raise HTTPException(status_code=400, detail="language parameter is required")

    if not file.filename:
        raise HTTPException(status_code=400, detail="Missing filename")

    suffix = os.path.splitext(file.filename)[1] or ".audio"

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name
            tmp.write(file.file.read())

        segments, info = model.transcribe(
            tmp_path,
            beam_size=beam_size,
            language=language,
            task="translate",   # ← IMPORTANT: streaming TRANSLATION
            vad_filter=True,
        )

        def event_generator():
            full_lines = []

            for i, seg in enumerate(segments):
                text = (seg.text or "").strip()
                full_lines.append(text)

                payload = {
                    "type": "segment",
                    "id": i,
                    "start": float(seg.start),
                    "end": float(seg.end),
                    "text": text,
                    "full_text": "\n".join(full_lines).strip(),
                }

                # SSE format
                yield f"data: {json.dumps(payload, ensure_ascii=False)}\n\n"

            # Signal completion
            yield "data: [DONE]\n\n"

        return StreamingResponse(
            event_generator(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
            },
        )

    finally:
        try:
            if "tmp_path" in locals() and os.path.exists(tmp_path):
                os.remove(tmp_path)
        except Exception:
            pass
