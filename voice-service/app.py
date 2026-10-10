"""API serwisu głosowego. Start: uv run uvicorn app:app --host 0.0.0.0 --port 8000"""
import io
from contextlib import asynccontextmanager

import torch
import torchaudio as ta
from fastapi import Depends, FastAPI, HTTPException, Request
from fastapi.security import APIKeyHeader
from fastapi.responses import Response
from pydantic import BaseModel, Field

import keys
from engine import Engine, NotFound
from script import parse_script

MAX_TEXT_CHARS = 1000
MAX_SCRIPT_CHARS = 3000
LINE_PAUSE_S = 0.5


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not keys.listing():
        raise RuntimeError("Brak kluczy API. Utwórz: uv run python genkey.py create <nazwa>")
    app.state.engine = Engine()
    yield


app = FastAPI(
    title="Serwis głosowy",
    description="Synteza mowy po polsku z klonowaniem głosu. Wszystkie endpointy poza `/health` wymagają nagłówka `X-API-Key`.",
    lifespan=lifespan,
)


api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False, description="Klucz z `genkey.py create`.")


def require_key(x_api_key: str | None = Depends(api_key_header)) -> str:
    name = keys.verify(x_api_key) if x_api_key else None
    if name is None:
        raise HTTPException(401, "Brak lub nieprawidłowy klucz API (nagłówek X-API-Key).")
    return name


def engine(request: Request) -> Engine:
    return request.app.state.engine


class TtsRequest(BaseModel):
    voice: str = Field(description="Identyfikator głosu (patrz `/voices`).", examples=["adrian"])
    character: str = Field(default="neutral", description="Identyfikator postaci (patrz `/characters`).", examples=["starzec"])
    text: str = Field(min_length=1, max_length=MAX_TEXT_CHARS, description="Tekst do wypowiedzenia.", examples=["Siadajcie bliżej, dzieci."])


class ScriptRequest(BaseModel):
    script: str = Field(
        min_length=1,
        max_length=MAX_SCRIPT_CHARS,
        description="Jedna lub więcej linii w formacie `[Głos, postać] Kwestia`.",
        examples=["[Adrian, starzec] Siadajcie bliżej, dzieci.\n[Kristina, wiedźma] Ha, trzymajcie się czapek!"],
    )


def wav_response(audio: torch.Tensor, sr: int) -> Response:
    buf = io.BytesIO()
    ta.save(buf, audio, sr, format="wav", encoding="PCM_S", bits_per_sample=16)
    # attachment: Swagger pokazuje wtedy link "Download file" zamiast odtwarzacza <audio>,
    # który ponawia zapytanie metodą GET (405 na endpointach POST).
    return Response(buf.getvalue(), media_type="audio/wav", headers={"Content-Disposition": 'attachment; filename="tts.wav"'})


@app.get("/health", summary="Stan serwisu", description="Bez klucza API. Zwraca używane urządzenie obliczeniowe.")
def health(request: Request):
    return {"status": "ok", "device": request.app.state.engine.device}


@app.get("/voices", summary="Lista głosów", dependencies=[Depends(require_key)])
def voices(eng: Engine = Depends(engine)):
    return {"voices": eng.voices()}


@app.get("/characters", summary="Lista postaci", dependencies=[Depends(require_key)])
def characters(eng: Engine = Depends(engine)):
    return {"characters": list(eng.characters)}


@app.post("/tts", summary="Synteza jednej kwestii", response_class=Response, dependencies=[Depends(require_key)])
def tts(req: TtsRequest, eng: Engine = Depends(engine)):
    try:
        audio = eng.synthesize(req.voice, req.character, req.text)
    except NotFound as e:
        raise HTTPException(404, str(e))
    return wav_response(audio, eng.sr)


@app.post("/tts/script", summary="Synteza skryptu z wieloma głosami", response_class=Response, dependencies=[Depends(require_key)])
def tts_script(req: ScriptRequest, eng: Engine = Depends(engine)):
    """Wiele linii `[Głos, postać] Kwestia` sklejonych w jedno nagranie `audio/wav`."""
    try:
        lines = parse_script(req.script)
    except ValueError as e:
        raise HTTPException(422, str(e))
    for line in lines:
        if len(line.text) > MAX_TEXT_CHARS:
            raise HTTPException(422, f"Linia przekracza {MAX_TEXT_CHARS} znaków.")
    pause = torch.zeros(1, int(LINE_PAUSE_S * eng.sr))
    pieces: list[torch.Tensor] = []
    try:
        for line in lines:
            pieces += [eng.synthesize(line.voice, line.character, line.text), pause]
    except NotFound as e:
        raise HTTPException(404, str(e))
    return wav_response(torch.cat(pieces[:-1], dim=-1), eng.sr)
