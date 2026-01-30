# Whisper Transcription System

This repository contains a high-performance speech-to-text transcription system utilizing `faster-whisper`. It is divided into a **FastAPI server** (optimized for Ubuntu/CUDA) and a **Streamlit client** (Mac/Frontend).

---

## 🚀 Quick Guide

To run the project quickly, add the following aliases to your `~/.zshrc` (or `~/.bashrc`) file:

### Ubuntu (Server)
```bash
# Add to .zshrc
alias whisper='cd /home/david/Documents/utils/ai/whisper-local'
alias whisper_server="cd /home/david/Documents/utils/ai/whisper-local/whisper-server && make run"
```
Run it with: `whisper_server`

### Mac (Client)
```bash
# Add to .zshrc
alias whisper='cd /Users/david/Documents/utils/ai/whisper'
alias whisper_client="cd /Users/david/Documents/utils/ai/whisper/whisper-client && make whisper_stream"
```
Run it with: `whisper_client`

---

## 🛠 Setup & Installation

### 1. Ubuntu (Server Side)

The server is designed to run on Ubuntu with CUDA support for fast inference. We need the ffmpeg toolkit.

```bash
sudo apt-get update && sudo apt-get install -y ffmpeg
```

#### Prerequisites & Environment
```bash
# Prepare directories
mkdir -p /home/david/Documents/utils/ai/whisper
sudo mkdir -p /mnt/ssd2/whisper
sudo chmod 777 /mnt/ssd2/whisper

# Navigate to server directory
cd /home/david/Documents/utils/ai/whisper/whisper-server

# Setup Python version
pyenv install -s 3.11.9
pyenv local 3.11.9
python -V

# Create virtual environment
uv venv
source .venv/bin/activate
```

#### Install Dependencies
```bash
uv pip install "fastapi>=0.110" "uvicorn[standard]>=0.27" python-multipart
uv pip install "faster-whisper>=1.1.0"
# Optional: CUDA support if needed
# uv pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"
```

#### Running the Server
```bash
# Start the FastAPI server
make run

# Health check
curl -s http://127.0.0.1:8765/health | python -m json.tool
```

---

### 2. Mac (Client Side)

The client provides a user-friendly Streamlit interface for transcription.

#### Prerequisites & Environment
```bash
# Prepare directory
mkdir -p /Users/david/Documents/utils/ai/whisper
cd /Users/david/Documents/utils/ai/whisper/whisper-client

# Setup Python version
pyenv install -s 3.11.9
pyenv local 3.11.9

# Create virtual environment
uv venv
source .venv/bin/activate
```

#### Install Dependencies
```bash
uv pip install "streamlit>=1.33" "requests>=2.31"
```

#### Running the Client
```bash
# For streaming transcription (Preferred)
make whisper_stream

# For simple bulk transcription
make whisper
```

---

## 📋 Dependency Summary

| Component | Main Dependencies | Command |
|-----------|-------------------|---------|
| **Server** | `fastapi`, `faster-whisper`, `uvicorn` | `uv pip install ...` |
| **Client** | `streamlit`, `requests` | `uv pip install ...` |

Use `uv` for significantly faster installation of Python packages compared to standard `pip`.