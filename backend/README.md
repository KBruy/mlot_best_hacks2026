# Backend

Osobny podserwis (FastAPI + PostgreSQL) w monorepo. Zarządzany przez [uv](https://docs.astral.sh/uv/); zależności są zablokowane w `uv.lock`. Wszystkie komendy uruchamiaj z katalogu `backend/`.

## Wymagania

- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- Docker z Compose, **uruchomiony** (dla bazy)

## Uruchomienie lokalne (API przez uv, baza w Dockerze)

```bash
cp .env.example .env
docker compose up -d --wait db          # baza; --wait czeka na healthcheck
uv sync                                 # tworzy .venv wg uv.lock
uv run --env-file .env python -m app.import_story   # tabela stories + upsert content/legend.json
uv run --env-file .env uvicorn app.main:app --reload
```

Sprawdzenie: `curl http://localhost:8000/api/health`.

## Wszystko w Dockerze (baza + API)

```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f api
```

## Zależności

```bash
uv add <pakiet>        # dodaje do pyproject.toml i aktualizuje uv.lock
uv lock --upgrade      # aktualizacja wersji w lockfile
```

Commituj `pyproject.toml` i `uv.lock`. Obraz Dockera instaluje zależności komendą `uv sync --locked`, więc build zawiedzie, jeśli lockfile jest nieaktualny.

## Baza

- `sql/` jest wykonywany przez Postgresa tylko przy tworzeniu pustego wolumenu. Po zmianie: `docker compose down -v && docker compose up -d`.
- `docker compose stop` zatrzymuje kontenery, `down` je usuwa (dane zostają), `down -v` usuwa także dane.
- Zajęty port 5432: ustaw `POSTGRES_PORT` w `.env` i dopasuj port w `DATABASE_URL`.
