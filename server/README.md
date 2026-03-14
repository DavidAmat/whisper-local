# Server

Check if the server is running
```bash
# UBUNTU (check if server is running, it should start automatically)
# otherwise run in ubuntu: ~/bin/start_whisper_server.sh
ss -ltnp | grep 8080
# LISTEN 0      5            0.0.0.0:8080       0.0.0.0:*    users:(("whisper-server",pid=687775,fd=3))
```

Run a simple test in Ubuntu:
```bash
~/bin/start_whisper_server.sh
# started whisper-server pid=634288 port=8080
curl localhost:8080
curl -X POST http://localhost:8080/inference \
-F "file=@/mnt/ssd2/whisper/whisper.cpp/samples/jfk.wav"
# Then stop it
~/bin/stop_whisper_server.sh
```