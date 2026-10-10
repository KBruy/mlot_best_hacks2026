"""Tworzy tabelę stories i importuje historie z content/*.json (upsert po id).

Każdy plik to jedna historia. Najpierw walidujemy wszystkie pliki (kontrakt
i graf, app.validate), potem zapisujemy je w jednej transakcji: jeden wadliwy
plik blokuje cały import. Usunięcie pliku nie usuwa historii z bazy.

Użycie (z katalogu backend/):
    uv run --env-file .env python -m app.import_story [plik.json ...]
"""
import sys

from psycopg.types.json import Jsonb

from . import db
from .validate import CONTENT_DIR, InvalidStory, load_story, story_paths


def main() -> None:
    paths = story_paths(sys.argv[1:])
    if not paths:
        sys.exit(f"Brak plików .json w {CONTENT_DIR}")
    stories = {}
    for path in paths:
        try:
            story = load_story(path)
        except InvalidStory as e:
            sys.exit(str(e))
        if story.id in stories:
            sys.exit(f"Powtórzone id historii {story.id!r}: {stories[story.id][0]} i {path}")
        stories[story.id] = (path, story)

    try:
        with db.connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS stories"
                " (id TEXT PRIMARY KEY, payload JSONB NOT NULL)"
            )
            for story_id, (_, story) in stories.items():
                conn.execute(
                    "INSERT INTO stories (id, payload) VALUES (%s, %s)"
                    " ON CONFLICT (id) DO UPDATE SET payload = EXCLUDED.payload",
                    (story_id, Jsonb(story.model_dump(exclude_none=True))),
                )
    except db.DatabaseUnavailable as e:
        sys.exit(f"Nie można połączyć się z bazą: {e}")
    for story_id, (path, _) in stories.items():
        print(f"Zaimportowano historię {story_id!r} z {path}")


if __name__ == "__main__":
    main()
