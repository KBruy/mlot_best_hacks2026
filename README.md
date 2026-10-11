# Żywy Bestiariusz Wrocławia

**Legenda, która dzieje się tam, gdzie stoisz.** Polskojęzyczna aplikacja webowa: interaktywny spacer fabularny
z legendą wrocławską w miejscu jej akcji. Telefon prowadzi gracza przez GPS, a gracz decyduje, jak potoczy się historia.

Projekt na BEST Hacks 2026 (Code For Culture, kategoria HISTORIA).

## O grze

Pierwsza legenda to **„Mostek Czarownic”**: od kościoła św. Marii Magdaleny po Rynek. Gracz jest najpierw panną, potem młodą czarownicą.

- **Na miejscu:** gra odblokowuje się w pobliżu kościoła. Wstęp zależy od strony, z której gracz patrzy, a niektóre sceny czekają, aż dojdzie do przystanku.
- **Decyzje z konsekwencjami:** 6 decyzji na każdej ścieżce, po 2–3 opcje. Każdy wybór ma skutek, gałęzie się łączą, a teksty pamiętają wcześniejsze wybory.
- **Nauka przez porównanie:** na końcu gracz poznaje zakończenie, oryginalną wersję legendy, fakty i rangę za liczbę wyborów zgodnych z legendą.
- **Lektor:** akapity są czytane z gotowych nagrań MP3 z napisami w stylu karaoke.
- Spacer z czytaniem trwa ok. 10 minut. Bez zgody na lokalizację albo daleko od miejsca aplikacja pokazuje zrozumiały komunikat.

Treści są pisane ręcznie przez zespół; aplikacja nie używa AI. Nowa legenda to nowy plik JSON w `content/`, bez zmian w kodzie.

## Technologie

| Warstwa                         | Stos                                                                                        |
| ------------------------------- | ------------------------------------------------------------------------------------------- |
| Frontend (`frontend/`)          | React 19, TypeScript, Vite, Tailwind CSS, Leaflet (OpenStreetMap), Geolocation API          |
| Backend (`backend/`)            | Python 3.12, FastAPI, Pydantic, PostgreSQL 16 (JSONB), Docker Compose, uv, pytest           |
| Synteza mowy (`voice-service/`) | FastAPI, Chatterbox Multilingual (PyTorch), klonowanie głosów członków zespołu za ich zgodą |
| Prototyp (`terminal-game/`)     | Python, gra w terminalu z symulowanym GPS; z niego pochodzi format historii                 |

Frontend pobiera wybraną historię z API **raz** i wszystkie przejścia wykonuje lokalnie; wybory nie trafiają na serwer.
Backend trzyma historie w tabeli `stories(id, payload JSONB)`, a przed importem waliduje cały graf fabuły
(brak cykli i martwych ścieżek, dokładnie 6 decyzji na każdej ścieżce, osiągalne zakończenia).

## Struktura

```text
frontend/        aplikacja React, nagrania i grafiki w public/
backend/         API, baza, importer i walidator historii, testy
content/*.json   historie (jeden plik = jedna historia; legend.json to neutralny fixture testów)
voice-service/   wewnętrzny serwis TTS, z którego przygotowano nagrania lektora
terminal-game/   prototyp terminalowy i opis formatu historii
docs/            dokumentacja API, one-pager, materiały
```

## Uruchomienie

Wymagania: [uv](https://docs.astral.sh/uv/), Docker z Compose, Node.js.

```bash
# 1. Baza, import treści i API (http://localhost:8000, Swagger: /docs)
cd backend
cp .env.example .env
docker compose up -d --wait db
uv sync
uv run --env-file .env python -m app.import_story
uv run --env-file .env uvicorn app.main:app --port 8000 --reload

# 2. Frontend (http://localhost:5173), w drugim terminalu
cd frontend
npm ci
npm run dev
```

Build i podgląd produkcyjny: `npm run build && npm run preview` (http://localhost:4173). Proxy `/api` do backendu działa w obu trybach.
Testy backendu: `uv run pytest` w `backend/` (bez Dockera). Szczegóły: [backend/README.md](backend/README.md).

voice-service jest opcjonalny: gra korzysta z gotowych nagrań w `frontend/public/audio/`. Uruchomienie: [voice-service/README.md](voice-service/README.md).

## API

Pełny opis połączeń frontend ↔ backend ↔ voice-service: [docs/API.md](docs/API.md).

| Endpoint                | Opis                                                                           |
| ----------------------- | ------------------------------------------------------------------------------ |
| `GET /api/stories`      | lista historii                                                                 |
| `GET /api/stories/{id}` | pełna historia (404 dla nieznanego id, 503 bez bazy)                           |
| `/api/voice/*`          | proxy do voice-service z kluczem trzymanym w backendzie (nieużywane przez grę) |

## Ograniczenia demo

- **Brak zapisu:** odświeżenie strony resetuje rozgrywkę. Nie ma kont ani wznawiania.
- **Offline:** po pobraniu historii kolejne decyzje nie wymagają sieci, ale ponowne otwarcie aplikacji bez sieci nie uruchomi gry.
- **GPS:** do testów poza miejscem legendy aplikacja ma tryb demo.
