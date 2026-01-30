SHELL := /bin/bash

APP_HOST ?= 0.0.0.0
APP_PORT ?= 8765

# Whisper config
WHISPER_MODEL ?= large-v3
WHISPER_DEVICE ?= cuda
WHISPER_COMPUTE_TYPE ?= float16
WHISPER_DOWNLOAD_ROOT ?= /mnt/ssd2/whisper

.PHONY: run health

run:
	@source .venv/bin/activate && \
	export APP_HOST=$(APP_HOST) APP_PORT=$(APP_PORT) && \
	export WHISPER_MODEL=$(WHISPER_MODEL) WHISPER_DEVICE=$(WHISPER_DEVICE) && \
	export WHISPER_COMPUTE_TYPE=$(WHISPER_COMPUTE_TYPE) WHISPER_DOWNLOAD_ROOT=$(WHISPER_DOWNLOAD_ROOT) && \
	uvicorn server:app --host $(APP_HOST) --port $(APP_PORT) --workers 1

health:
	@curl -s http://127.0.0.1:8765/health | python -m json.tool

stream_test:
	@curl -N -X POST "http://127.0.0.1:$(APP_PORT)/translate_stream?language=es" \
		-F "file=@/path/to/test.aac"