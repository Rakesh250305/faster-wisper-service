from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import shutil, uuid, os

app = FastAPI()
model = WhisperModel("small", compute_type="int8")

@app.get("/")
def health():
    return {"status": "ok"}

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    temp_dir = "/tmp"
    os.makedirs(temp_dir, exist_ok=True)
    
    file_path = f"{temp_dir}/{uuid.uuid4()}.webm"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    segments, info = model.transcribe(
        file_path,
        language=None,
        vad_filter=True
    )

    os.remove(file_path)

    text = " ".join([seg.text for seg in segments])
    avg_logprob = sum(seg.avg_logprob for seg in segments) / len(segments)

    # Normalize to 0–1 range
    confidence = max(0, min(1, (avg_logprob + 1) / 1))
    # confidence = round(
    #     sum(seg.avg_logprob for seg in segments) / len(segments),
    #     2
    # )

    return {
        "text": text.strip(),
        "language": info.language,
        "confidence": round(confidence, 2),
    }
