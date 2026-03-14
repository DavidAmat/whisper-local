#!/usr/bin/env bash
set -euo pipefail

PORT="${1:-8080}"

WHISPER_DIR="/mnt/ssd2/whisper/whisper.cpp"
MODEL="${MODEL:-$WHISPER_DIR/models/ggml-large-v3.bin}"

LOG="${LOG:-$HOME/whisper-server.log}"
PIDFILE="${PIDFILE:-$HOME/whisper-server.pid}"

cd "$WHISPER_DIR"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "whisper-server already running on PID $(cat "$PIDFILE")"
  exit 0
fi

# Good stable defaults for multilingual transcription.
# Per-request fields from the client will override these when sent.
nohup ./build/bin/whisper-server \
  --host 0.0.0.0 \
  --port "$PORT" \
  -m "$MODEL" \
  -l auto \
  -bs 5 \
  -bo 5 \
  -mc 512 \
  -ac 0 \
  -et 2.40 \
  -lpt -1.00 \
  -nth 0.60 \
  -sns \
  > "$LOG" 2>&1 &

echo $! > "$PIDFILE"
sleep 1

if ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "failed to start whisper-server"
  exit 1
fi

echo "started whisper-server pid=$(cat "$PIDFILE") port=$PORT model=$MODEL"