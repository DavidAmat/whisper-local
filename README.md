# Ubuntu

```bash
mkdir -p /home/david/Documents/utils/ai/whisper
sudo mkdir -p /mnt/ssd2/whisper
sudo chmod 777 /mnt/ssd2/whisper
cd /home/david/Documents/utils/ai/whisper

pyenv install -s 3.11.9
pyenv local 3.11.9
python -V
uv venv
source .venv/bin/activate

uv pip install "fastapi>=0.110" "uvicorn[standard]>=0.27" python-multipart
uv pip install "faster-whisper>=1.1.0"
uv pip install nvidia-cublas-cu12 "nvidia-cudnn-cu12==9.*"

# Create the loadtest.py

# Run
make run

# Check 
curl -s http://127.0.0.1:8765/health | python -m json.tool

```

# Mac

```bash
mkdir -p /Users/david/Documents/utils/ai/whisper
cd /Users/david/Documents/utils/ai/whisper

pyenv install -s 3.11.9
pyenv local 3.11.9
uv venv
source .venv/bin/activate

uv pip install "streamlit>=1.33" "requests>=2.31"

make whisper # if you want simple bulk transcription
make whisper_streaming. # if you want streaming transcription

```