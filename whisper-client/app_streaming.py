import os
import json
import requests
import streamlit as st

# -------------------------
# Configuration
# -------------------------
DEFAULT_SERVER = os.getenv("WHISPER_SERVER_URL", "http://192.168.0.112:8765")

LANG_CHOICES = [
    "en", "es", "fr", "de", "it", "pt", "nl",
    "ca", "eu", "gl",
    "zh", "ja", "ko",
    "ar", "hi", "ru", "uk", "tr",
]

# -------------------------
# Page setup
# -------------------------
st.set_page_config(page_title="Whisper Streaming Translation", layout="centered")

st.markdown(
    """
    <style>
      .chat-wrap {max-width: 900px; margin: 0 auto;}
      .bubble {
        padding: 12px 14px;
        border-radius: 14px;
        margin: 8px 0;
        border: 1px solid rgba(120,120,120,.25);
        background: rgba(120,120,120,.06);
        font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial;
        white-space: pre-wrap;
      }
      .meta {
        font-size: 12px;
        opacity: 0.7;
        margin-top: 6px;
      }
      .header {
        font-size: 18px;
        font-weight: 650;
        margin: 8px 0 2px 0;
      }
      .sub {
        font-size: 13px;
        opacity: 0.75;
        margin-bottom: 12px;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# UI Header
# -------------------------
st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
st.markdown('<div class="header">Whisper – Streaming Transcription & Translation</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Live, segment-by-segment processing powered by your GPU server.</div>',
    unsafe_allow_html=True,
)

# -------------------------
# Controls
# -------------------------
with st.expander("Server & processing settings", expanded=False):
    server_url = st.text_input("Server URL", value=DEFAULT_SERVER)
    col1, col2 = st.columns(2)
    with col1:
        language = st.selectbox(
            "Audio language (required)",
            LANG_CHOICES,
            index=1 if "es" in LANG_CHOICES else 0,
        )
    with col2:
        task = st.selectbox(
            "Task",
            ["transcribe", "translate"],
            index=0,
            help="'transcribe' keeps the original language. 'translate' converts to English."
        )
    show_timestamps = st.toggle("Show timestamps", value=True)

uploaded = st.file_uploader(
    "Audio file",
    type=["aac", "m4a", "mp3", "wav", "mp4", "caf"],
)

start = st.button(
    "▶ Start streaming",
    type="primary",
    use_container_width=True,
    disabled=(uploaded is None),
)

st.divider()

# -------------------------
# Streaming logic
# -------------------------
def fmt_ts(seconds: float) -> str:
    m = int(seconds // 60)
    s = seconds - m * 60
    return f"{m:02d}:{s:06.3f}"


if start and uploaded is not None:
    bubble = st.empty()
    meta = st.empty()

    lines = []

    with st.spinner("Streaming translation from GPU…"):
        try:
            files = {
                "file": (
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type or "application/octet-stream",
                )
            }

            with requests.post(
                f"{server_url.rstrip('/')}/stream",
                files=files,
                params={"language": language, "task": task},
                stream=True,
                timeout=600,
                headers={"Accept": "text/event-stream"},
            ) as r:
                r.raise_for_status()

                for raw in r.iter_lines(decode_unicode=True):
                    if not raw:
                        continue

                    if not raw.startswith("data: "):
                        continue

                    payload = raw[len("data: "):]

                    if payload == "[DONE]":
                        break

                    evt = json.loads(payload)

                    if show_timestamps:
                        line = (
                            f"[{fmt_ts(evt['start'])} → {fmt_ts(evt['end'])}] "
                            f"{evt['text']}"
                        )
                    else:
                        line = evt["text"]

                    lines.append(line)

                    full_text = "\n".join(lines)
                    bubble.markdown(
                        f'<div class="bubble">{full_text}</div>',
                        unsafe_allow_html=True,
                    )

                meta.markdown(
                    f'<div class="meta">File: {uploaded.name} · Source language: {language} · '
                    f'Task: {task}</div>',
                    unsafe_allow_html=True,
                )

        except requests.RequestException as e:
            st.error(f"Streaming request failed: {e}")

st.markdown("</div>", unsafe_allow_html=True)
