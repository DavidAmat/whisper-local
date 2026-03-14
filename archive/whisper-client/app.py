import os

import requests
import streamlit as st

DEFAULT_SERVER = os.getenv("WHISPER_SERVER_URL", "http://192.168.0.112:8765")

st.set_page_config(page_title="Whisper STT", layout="centered")

# --- Minimal chat-like styling ---
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

if "conversation" not in st.session_state:
    st.session_state.conversation = (
        []
    )  # list of dicts: {filename, text, timestamped_text, segments}

st.markdown('<div class="chat-wrap">', unsafe_allow_html=True)
st.markdown('<div class="header">Whisper STT</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="sub">Upload an audio file and transcribe on your Ubuntu GPU server.</div>',
    unsafe_allow_html=True,
)

with st.expander("Server settings", expanded=False):
    server_url = st.text_input(
        "Server URL", value=DEFAULT_SERVER, help="Example: http://192.168.0.112:8765"
    )
    show_timestamps = st.toggle("Show timestamps in chat", value=True)
    word_timestamps = st.toggle("Word timestamps (slower)", value=False)

# Language
LANG_CHOICES = [
    "en",
    "es",
    "fr",
    "de",
    "it",
    "pt",
    "nl",
    "ca",
    "eu",
    "gl",
    "zh",
    "ja",
    "ko",
    "ar",
    "hi",
    "ru",
    "uk",
    "tr",
]
language = st.selectbox(
    "Audio language (required)", LANG_CHOICES, index=1
)  # e.g. default "es"


col_a, col_b = st.columns([1, 1])
with col_a:
    uploaded = st.file_uploader(
        "Audio file", type=["aac", "m4a", "mp3", "wav", "mp4", "caf"]
    )
with col_b:
    st.write("")
    st.write("")
    if st.button("🧹 Clear conversation", use_container_width=True):
        st.session_state.conversation = []
        st.rerun()

do_transcribe = st.button(
    "Transcribe", type="primary", use_container_width=True, disabled=(uploaded is None)
)


def render_message(msg: dict, show_ts: bool):
    # Render a single assistant bubble
    body = msg["timestamped_text"] if show_ts else msg["text"]
    st.markdown(f'<div class="bubble">{body}</div>', unsafe_allow_html=True)
    st.markdown(
        f'<div class="meta">File: {msg.get("filename","")} · Language: {msg.get("language","?")}</div>',
        unsafe_allow_html=True,
    )


if do_transcribe and uploaded is not None:
    with st.spinner("Uploading + transcribing on GPU…"):
        try:
            files = {
                "file": (
                    uploaded.name,
                    uploaded.getvalue(),
                    uploaded.type or "application/octet-stream",
                )
            }
            params = {
                "timestamps": True,
                "word_timestamps": bool(word_timestamps),
                "language": language,
            }
            r = requests.post(
                f"{server_url.rstrip('/')}/transcribe",
                files=files,
                params=params,
                timeout=600,
            )
            r.raise_for_status()
            data = r.json()
            st.session_state.conversation.append(data)
        except requests.RequestException as e:
            st.error(f"Request failed: {e}")

# Conversation rendering
st.divider()
if not st.session_state.conversation:
    st.info("No transcriptions yet. Upload a file and click Transcribe.")
else:
    for msg in st.session_state.conversation:
        render_message(msg, show_timestamps)

    # Copy-friendly outputs from the most recent message
    latest = st.session_state.conversation[-1]
    st.divider()
    st.subheader("Copy")
    with st.expander("Plain text (no timestamps)", expanded=False):
        st.code(latest.get("text", ""), language="text")
    with st.expander("Timestamped text", expanded=True):
        st.code(latest.get("timestamped_text", ""), language="text")

st.markdown("</div>", unsafe_allow_html=True)
