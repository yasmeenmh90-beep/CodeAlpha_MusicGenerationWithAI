from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pathlib import Path
from uuid import uuid4, UUID
from threading import Lock
import music
import conditioning
from typing import Literal
from fastapi import HTTPException

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
    root: int = Field(0, ge=0, le=11)
    scale: Literal["chromatic","major","minor","pentatonic"] = "chromatic"
    genre: Literal["ambient","classical","electronic","jazz","cinematic","lofi"] | None = None

@app.get("/health")
def health():
    return {"model_ready": (music.ROOT / "model.pt").is_file(), "conditioned_ready": conditioning.CHECKPOINT.is_file()}

@app.post("/generate")
def generate(settings: Settings):
    ROOT.mkdir(exist_ok=True)
    key = str(uuid4())
    with lock:
        params = settings.model_dump(exclude={"root","scale","genre"})
        if settings.genre:
            if not conditioning.CHECKPOINT.is_file():
                raise HTTPException(409, "Train the genre-conditioned checkpoint first")
            midi, tokens = conditioning.generate(settings.genre, **params)
        else:
            midi, tokens = music.generate(**params)
        midi, tokens = conditioning.constrain(midi, tokens, settings.root, settings.scale)
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

@app.get("/training/history")
def training_history():
    import json
    def read(name):
        path = music.ROOT / name
        return json.loads(path.read_text()) if path.is_file() else []
    return {"original": read("history.json"), "conditioned": read("conditioned_history.json")}
