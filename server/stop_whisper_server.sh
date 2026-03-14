#!/usr/bin/env bash
set -euo pipefail

PIDFILE="${PIDFILE:-$HOME/whisper-server.pid}"

if [ ! -f "$PIDFILE" ]; then
  echo "whisper-server is not running"
  exit 0
fi

PID="$(cat "$PIDFILE")"

if kill -0 "$PID" 2>/dev/null; then
  kill "$PID"
  rm -f "$PIDFILE"
  echo "stopped whisper-server pid=$PID"
else
  rm -f "$PIDFILE"
  echo "removed stale pidfile"
fi