SHELL := /bin/bash

.PHONY: whisper whisper_stream

# Standard (non-streaming) transcription UI
whisper:
	@source .venv/bin/activate && \
	streamlit run app.py

# Streaming translation UI
whisper_stream:
	@source .venv/bin/activate && \
	streamlit run app_streaming.py
