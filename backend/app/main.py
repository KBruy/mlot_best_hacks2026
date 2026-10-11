from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel, Field

from . import db, voice
from .models import Story, StorySummary

app = FastAPI(
    title="Legendy wrocławskie — API",
    description="Odczyt historii z PostgreSQL. Wybory gracza nie są wysyłane do serwera. "
    "Endpointy `/api/voice/*` przekazują zapytania do voice-service z kluczem API trzymanym w backendzie.",
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

DB_UNAVAILABLE = "Baza danych jest niedostępna."


class ErrorMessage(BaseModel):
    detail: str


RESPONSE_503 = {503: {"model": ErrorMessage, "description": DB_UNAVAILABLE}}


@app.get("/api/health", summary="Czy API działa (bez sprawdzania bazy)")
def health():
    return {"status": "ok"}


@app.get(
    "/api/stories",
    response_model=list[StorySummary],
    summary="Lista historii",
    description="Krótki opis każdej historii w bazie, bez grafu. Pusta lista przed pierwszym importem.",
    responses=RESPONSE_503,
)
def read_stories():
    try:
        return db.list_stories()
    except db.DatabaseUnavailable:
        raise HTTPException(503, DB_UNAVAILABLE)


# Historia jest walidowana przy imporcie, więc zwracamy JSON prosto z bazy;
# response_model służy tylko dokumentacji (/docs).
@app.get(
    "/api/stories/{story_id}",
    response_model=Story,
    summary="Pełna historia",
    description="Cały dokument historii (lokalizacja, stan, sceny, zakończenia). Pobierany raz; przejścia wykonuje frontend.",
    responses={404: {"model": ErrorMessage, "description": "Nie ma takiej historii."}, **RESPONSE_503},
)
def read_story(story_id: str):
    try:
        story = db.get_story_json(story_id)
    except db.DatabaseUnavailable:
        raise HTTPException(503, DB_UNAVAILABLE)
    if story is None:
        raise HTTPException(404, "Nie ma takiej historii.")
    return Response(story, media_type="application/json")


VOICE_UNAVAILABLE = "Serwis głosu jest niedostępny."
VOICE_TIMEOUT = "Serwis głosu nie odpowiedział na czas."
VOICE_BAD_KEY = "Backend ma nieprawidłowy klucz voice-service."

VOICE_ERRORS = {
    502: {"model": ErrorMessage, "description": VOICE_BAD_KEY},
    503: {"model": ErrorMessage, "description": VOICE_UNAVAILABLE},
    504: {"model": ErrorMessage, "description": VOICE_TIMEOUT},
}
AUDIO_RESPONSE = {200: {"content": {"audio/wav": {}}, "description": "Nagranie WAV (PCM 16-bit, mono, 24 kHz)."}}


# Te same pola i limity co w voice-service (voice-service/API.md): złe dane odrzucamy od razu.
class TtsRequest(BaseModel):
    voice: str = Field(examples=["adrian"])
    character: str = Field(default="neutral", examples=["starzec"])
    text: str = Field(min_length=1, max_length=1000, examples=["Siadajcie bliżej, dzieci."])


class ScriptRequest(BaseModel):
    script: str = Field(min_length=1, max_length=3000, examples=["[Adrian, starzec] Siadajcie bliżej, dzieci."])


def proxy_voice(method: str, path: str, body: BaseModel | None = None) -> Response:
    try:
        status, content_type, content = voice.request(method, path, None if body is None else body.model_dump())
    except voice.VoiceTimeout:
        raise HTTPException(504, VOICE_TIMEOUT)
    except voice.VoiceUnavailable:
        raise HTTPException(503, VOICE_UNAVAILABLE)
    # 401 dotyczy klucza backendu, nie gracza; pozostałe kody (404, 422, 500) przekazujemy bez zmian.
    if status == 401:
        raise HTTPException(502, VOICE_BAD_KEY)
    return Response(content, status, media_type=content_type)


@app.get("/api/voice/health", summary="Stan voice-service", responses=VOICE_ERRORS)
def voice_health():
    return proxy_voice("GET", "/health")


@app.get("/api/voice/voices", summary="Lista głosów voice-service", responses=VOICE_ERRORS)
def voice_voices():
    return proxy_voice("GET", "/voices")


@app.get("/api/voice/characters", summary="Lista postaci voice-service", responses=VOICE_ERRORS)
def voice_characters():
    return proxy_voice("GET", "/characters")


@app.post(
    "/api/voice/tts",
    summary="Synteza jednej kwestii",
    description="Przekazuje do `POST /tts` voice-service. Generacja może trwać kilkadziesiąt sekund.",
    response_class=Response,
    responses={**AUDIO_RESPONSE, **VOICE_ERRORS},
)
def voice_tts(req: TtsRequest):
    return proxy_voice("POST", "/tts", req)


@app.post(
    "/api/voice/tts/script",
    summary="Synteza skryptu z wieloma głosami",
    description="Przekazuje do `POST /tts/script` voice-service. Linie w formacie `[Głos, postać] Kwestia`.",
    response_class=Response,
    responses={**AUDIO_RESPONSE, **VOICE_ERRORS},
)
def voice_tts_script(req: ScriptRequest):
    return proxy_voice("POST", "/tts/script", req)
