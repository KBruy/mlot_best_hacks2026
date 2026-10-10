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
uv run --env-file .env python -m app.import_story   # tabela stories + upsert content/*.json
uv run --env-file .env uvicorn app.main:app --reload
```

Sprawdzenie: `curl http://localhost:8000/api/health`, dokumentacja endpointów: http://localhost:8000/docs.

## API

| Endpoint | Zwraca |
|---|---|
| `GET /api/stories` | lista `[{id, title, intro}]` (pusta przed importem) |
| `GET /api/stories/{id}` | pełna historia zgodna z `app/models.py`; 404 dla nieznanego `id` |

Niedostępna baza daje 503 na obu endpointach. Frontend pobiera wybraną historię raz i gra lokalnie.

Opcjonalne pole `audio_url` (w scenie, finale i opcji — nagranie konsekwencji) to ścieżka do gotowego pliku audio serwowanego statycznie przez frontend, np. `/audio/<id historii>/<id węzła>.wav` z `frontend/public/audio/`. Pole może nie występować; backend nie przechowuje plików audio.

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

- Tabela `stories(id, payload JSONB)` powstaje przy imporcie. Import bierze wszystkie `content/*.json` (albo pliki podane w argumentach), waliduje je modelami z `app/models.py` i robi upsert po `id` w jednej transakcji; jeden wadliwy plik blokuje cały import. Można go powtarzać.
- Jeden plik = jedna historia; `id` musi być stałe (zmiana `id` tworzy nową historię). Usunięcie pliku nie usuwa historii z bazy.
- Import uruchamiaj z hosta (komenda wyżej) także wtedy, gdy API działa w Dockerze; `.env` wskazuje bazę przez `localhost`.
- `docker compose stop` zatrzymuje kontenery, `down` je usuwa (dane zostają), `down -v` usuwa także dane.
- Zajęty port 5432: ustaw `POSTGRES_PORT` w `.env` i dopasuj port w `DATABASE_URL`.
