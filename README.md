# Whisper Transcription System

This repository contains a high performance speech to text transcription system using faster-whisper. It is divided into a FastAPI server and a Streamlit client.

## Quick Guide

To run the project quickly, add the following aliases to your shell configuration file.

### Ubuntu Server

```bash
alias whisper='cd /home/david/Documents/utils/ai/whisper-local'
alias whisper_server="cd /home/david/Documents/utils/ai/whisper-local/whisper-server && make run"
```

Run it with: whisper_server

### Mac Client

```bash
alias whisper='cd /Users/david/Documents/utils/ai/whisper'
alias whisper_client="cd /Users/david/Documents/utils/ai/whisper/whisper-client && make whisper_stream"
```

Run it with: whisper_client

## Setup and Installation

### Ubuntu Server Side

The server is designed to run on Ubuntu with CUDA support for fast inference. You must install ffmpeg.

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

### Server Environment Setup

```bash
mkdir -p /home/david/Documents/utils/ai/whisper
sudo mkdir -p /mnt/ssd2/whisper
sudo chmod 777 /mnt/ssd2/whisper

cd /home/david/Documents/utils/ai/whisper/whisper-server
pyenv install -s 3.11.9
pyenv local 3.11.9
uv venv
source .venv/bin/activate
```

### Install Server Dependencies

```bash
uv pip install "fastapi>=0.110" "uvicorn[standard]>=0.27" python-multipart
uv pip install "faster-whisper>=1.1.0"
```

### Running the Server

Start the FastAPI server:

```bash
make run
```

Health check:

```bash
curl -s http://127.0.0.1:8765/health
```

### Mac Client Side

The client provides a Streamlit interface for transcription.

### Client Environment Setup

```bash
mkdir -p /Users/david/Documents/utils/ai/whisper
cd /Users/david/Documents/utils/ai/whisper/whisper-client

pyenv install -s 3.11.9
pyenv local 3.11.9
uv venv
source .venv/bin/activate
```

### Install Client Dependencies

```bash
uv pip install "streamlit>=1.33" "requests>=2.31"
```

### Running the Client

Start the streaming interface:

```bash
make whisper_stream
```

Start the standard interface:

```bash
make whisper
```

## System Architecture and Communication

### Server Logic

The server.py file utilizes the FastAPI framework and the faster-whisper library. When the server starts, it loads the Whisper model (defaulting to large-v3) into GPU memory. This ensures that transcription requests are handled with high efficiency.

### Client Logic

The app_streaming.py file uses Streamlit to create a web interface. It handles file uploads and communicates with the server using the requests library. It specifically uses the stream=True parameter to handle Server-Sent Events (SSE), allowing the UI to update as soon as a new text segment is processed by the server.

### Communication Payload

To make the system work, the client sends a POST request to the /stream endpoint.

Request Method: POST
Content-Type: multipart/form-data

The following items must be submitted in the request:

1. File: A binary audio file (mp3, wav, aac, etc.) sent in the multipart body with the key "file".
2. Language: Sent as a query parameter "language" (e.g., es, en).
3. Task: Sent as a query parameter "task". Use "transcribe" to get text in the original language or "translate" to get an English translation.

### Server Response

The server responds with a text/event-stream. Each event contains a JSON payload with the following structure:

```json
{
  "type": "segment",
  "id": 0,
  "start": 0.0,
  "end": 2.5,
  "text": "Hello world",
  "full_text": "Hello world"
}
```

The stream ends with a data: [DONE] message.

## Dependency Summary

Server: fastapi, faster-whisper, uvicorn, python-multipart.
Client: streamlit, requests.
Requirements: ffmpeg installed on the server system.