from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.gzip import GZipMiddleware

from . import db
from .models import Story, StorySummary

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=1000)

DB_UNAVAILABLE = "Baza danych jest niedostępna."


@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.get("/api/stories", response_model=list[StorySummary])
def read_stories():
    try:
        return db.list_stories()
    except db.DatabaseUnavailable:
        raise HTTPException(503, DB_UNAVAILABLE)


# Historia jest walidowana przy imporcie, więc zwracamy JSON prosto z bazy;
# response_model służy tylko dokumentacji (/docs).
@app.get("/api/stories/{story_id}", response_model=Story)
def read_story(story_id: str):
    try:
        story = db.get_story_json(story_id)
    except db.DatabaseUnavailable:
        raise HTTPException(503, DB_UNAVAILABLE)
    if story is None:
        raise HTTPException(404, "Nie ma takiej historii.")
    return Response(story, media_type="application/json")
