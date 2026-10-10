"""Tworzy tabelę stories i importuje content/legend.json (upsert).

Użycie (z katalogu backend/, z ustawionym DATABASE_URL):
    python -m app.import_story [ścieżka/do/legend.json]
"""
import json
import sys
from pathlib import Path

from psycopg.types.json import Jsonb

from . import db

DEFAULT_PATH = Path(__file__).resolve().parents[2] / "content" / "legend.json"


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    story = json.loads(path.read_text(encoding="utf-8"))
    with db.connect() as conn:
        conn.execute(
            "CREATE TABLE IF NOT EXISTS stories"
            " (id TEXT PRIMARY KEY, payload JSONB NOT NULL)"
        )
        conn.execute(
            "INSERT INTO stories (id, payload) VALUES (%s, %s)"
            " ON CONFLICT (id) DO UPDATE SET payload = EXCLUDED.payload",
            (story["id"], Jsonb(story)),
        )
    print(f"Zaimportowano historię {story['id']!r} z {path}")


if __name__ == "__main__":
    main()
