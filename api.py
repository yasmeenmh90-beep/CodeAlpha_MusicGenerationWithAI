from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from uuid import uuid4, UUID
from threading import Lock
import music

app = FastAPI(title="SonataAI Studio")
app.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173","http://127.0.0.1:5173"], allow_methods=["GET","POST"], allow_headers=["*"])
ROOT = Path(__file__).resolve().parent / "studio_outputs"
lock = Lock()

class Settings(BaseModel):
    bpm: int = Field(100, ge=30, le=240)
    temperature: float = Field(.9, gt=0, le=3)
    length: int = Field(128, ge=16, le=512)
    program: int = Field(0, ge=0, le=127)
    seed: int = Field(42, ge=0, le=2147483647)

@app.get("/health")
def health():
    return {"model_ready": (music.ROOT / "model.pt").is_file()}

@app.post("/generate")
def generate(settings: Settings):
    ROOT.mkdir(exist_ok=True)
    key = str(uuid4())
    with lock:
        midi, tokens = music.generate(**settings.model_dump())
        music.export(midi, ROOT / key)
    return {"id": key, "wav": f"/tracks/{key}/wav", "midi": f"/tracks/{key}/mid", "duration": midi.get_end_time(), "tokens": tokens}

@app.get("/tracks/{key}/{kind}")
def track(key: UUID, kind: str):
    from fastapi import HTTPException
    if kind not in ("wav", "mid"):
        raise HTTPException(404)
    path = ROOT / f"{key}.{kind}"
    if not path.is_file():
        raise HTTPException(404)
    return FileResponse(path, media_type="audio/wav" if kind=="wav" else "audio/midi")
