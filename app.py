from fastapi import FastAPI, UploadFile, File
from faster_whisper import WhisperModel
import shutil, uuid, os, gc

app = FastAPI()

model = WhisperModel(
    "tiny",
    device="cpu",
    compute_type="int8",
    cpu_threads=2,
    num_workers=1
)

@app.post("/transcribe")
async def transcribe(audio: UploadFile = File(...)):
    os.makedirs("/tmp", exist_ok=True)
    file_path = f"/tmp/{uuid.uuid4()}.webm"

    with open(file_path, "wb") as f:
        shutil.copyfileobj(audio.file, f)

    segments, info = model.transcribe(
        file_path,
        vad_filter=True,
        beam_size=1,
        best_of=1
    )

    text = " ".join(seg.text for seg in segments)

    confidence = round(
        sum(seg.avg_logprob for seg in segments) / max(len(segments), 1),
        2
    )

    os.remove(file_path)
    gc.collect()

    return {
        "text": text.strip(),
        "language": info.language,
        "confidence": confidence
    }


gc.collect()

