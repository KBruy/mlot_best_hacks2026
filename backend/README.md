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
uv run --env-file .env python -m app.import_story  # tabela stories + upsert content/*.json
uv run --env-file .env uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Sprawdzenie: `curl http://localhost:8000/api/health`, dokumentacja endpointów: http://localhost:8000/docs.

## API

| Endpoint                | Zwraca                                                           |
| ----------------------- | ---------------------------------------------------------------- |
| `GET /api/stories`      | lista `[{id, title, intro: {title, paragraphs}}]` (pusta przed importem) |
| `GET /api/stories/{id}` | pełna historia zgodna z `app/models.py`; 404 dla nieznanego `id` |

Niedostępna baza daje 503 na obu endpointach. Frontend pobiera wybraną historię raz i gra lokalnie.

Format historii pochodzi z prototypu `terminal-game/` (opis pól: `terminal-game/docs/FORMAT_HISTORII.md`), z dodanymi `id` i `title`. Frontend sam rozwiązuje teksty z warunkami `if` na podstawie stanu (`state`, ustawiany przez `set` w opcjach; pole `widok` ustawia z GPS: id punktu widokowego albo `location.default_view`) i wybiera zakończenie po polach `ending_by`, gdy opcja ma `next: null`. Pola zaczynające się od `_` (np. `_note`) to notatki: walidator i import je pomijają.

Opcjonalne pole `audio_url` jest przy pojedynczym akapicie albo wariancie tekstu (`{"if"?, "text", "audio_url"}`): każdy czytany akapit ma własne nagranie MP3 `/audio/<id historii>/<plik>.mp3` serwowane statycznie przez frontend z `frontend/public/audio/`. Teksty opcji nie są czytane. Obok może leżeć `<plik>.json` ze znacznikami czasu słów (karaoke). Backend nie przechowuje plików audio; przypisanie głosów: `voice-service/NARRACJA.md`.

## Wszystko w Dockerze (baza + API)

```bash
cp .env.example .env
docker compose up -d --build
docker compose logs -f api
```

## Walidacja i testy

```bash
uv run python -m app.validate        # sprawdza content/*.json bez bazy (albo podane pliki)
uv run pytest                        # walidator, modele i API; bez Dockera
```

Walidator sprawdza kontrakt (typy, brak dodatkowych pól poza notatkami `_...`) i graf: istniejące `start`, cele `next` i przystanki `before`, 2–3 opcje na scenę, warunki `if` i `set` tylko z pól i wartości z `state`, `audio_url` w ścieżce `/audio/<id>/…mp3` (jeden plik na jeden tekst, bez nagrań tekstów opcji), `location.default_view` i punkty widokowe w `state.widok`, brak cykli, osiągalność wszystkich scen, dokładnie 6 decyzji na każdej ścieżce, ustalenie pól `ending_by` na każdej ścieżce, istniejące i osiągalne zakończenie dla każdej kombinacji ich wartości oraz rangę z `min: 0`. Import uruchamia tę samą walidację przed zapisem.

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
