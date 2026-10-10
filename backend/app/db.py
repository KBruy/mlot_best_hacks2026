import os

import psycopg
from psycopg.rows import dict_row


class DatabaseUnavailable(Exception):
    pass


def connect() -> psycopg.Connection:
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise DatabaseUnavailable("Brak DATABASE_URL (sprawdź plik .env).")
    try:
        return psycopg.connect(url, row_factory=dict_row, connect_timeout=3)
    except psycopg.OperationalError as e:
        raise DatabaseUnavailable(str(e)) from e


def _fetch(query: str, params: tuple = ()) -> list[dict]:
    """Brak tabeli stories (przed pierwszym importem) traktujemy jak brak historii."""
    try:
        with connect() as conn:
            return conn.execute(query, params).fetchall()
    except psycopg.errors.UndefinedTable:
        return []
    except psycopg.OperationalError as e:
        raise DatabaseUnavailable(str(e)) from e


def list_stories() -> list[dict]:
    return _fetch(
        "SELECT id, payload->>'title' AS title, payload->'intro' AS intro"
        " FROM stories ORDER BY id"
    )


def get_story_json(story_id: str) -> str | None:
    """Pełna historia jako gotowy tekst JSON, bez parsowania w Pythonie."""
    rows = _fetch("SELECT payload::text AS payload FROM stories WHERE id = %s", (story_id,))
    return rows[0]["payload"] if rows else None
