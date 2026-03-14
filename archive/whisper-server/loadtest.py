from faster_whisper import WhisperModel

print("Loading model...")
m = WhisperModel(
    "large-v3",
    device="cuda",
    compute_type="float16",
    download_root="/mnt/ssd2/whisper",
)
print("Model loaded OK on GPU")