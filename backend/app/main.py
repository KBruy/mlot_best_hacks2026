from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel

from . import db
from .models import Story, StorySummary

app = FastAPI(
    title="Legendy wrocławskie — API",
    description="Odczyt historii z PostgreSQL. Wybory gracza nie są wysyłane do serwera.",
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
    description="Cały dokument historii (postaci i wszystkie węzły). Pobierany raz; przejścia wykonuje frontend.",
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
