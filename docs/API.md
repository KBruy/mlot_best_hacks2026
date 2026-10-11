# API: frontend, backend i voice-service

Jeden dokument dla wszystkich połączeń w projekcie. Typy pól są zawsze aktualne w Swaggerze:
backend `http://localhost:8000/docs`, voice-service `http://localhost:8001/docs`.
Ten plik opisuje, kto z kim rozmawia, jakie są kody błędów, ile to trwa i jak tego używać.

## 1. Architektura

```
                    /api/stories...      ┌──────────────┐   SQL    ┌────────────┐
 ┌──────────────┐ ─────────────────────► │              │ ───────► │ PostgreSQL │
 │  Frontend    │                        │ Backend gry  │          └────────────┘
 │  (React PWA) │   /api/voice/...       │ FastAPI :8000│  X-API-Key  ┌───────────────┐
 │  :5173/:4173 │ ─────────────────────► │              │ ──────────► │ voice-service │
 └──────────────┘                        └──────────────┘             │ FastAPI :8001 │
        │ /audio/..., /art/... (pliki statyczne frontendu)            └───────────────┘
        ▼
  frontend/public/
```

| Połączenie | Kto woła | Autoryzacja | Sekcja |
|---|---|---|---|
| Frontend → backend (`/api/stories*`) | przeglądarka | brak | [2](#2-frontend--backend-historie) |
| Backend → voice-service | backend | `X-API-Key` z `backend/.env` | [3](#3-backend--voice-service) |
| Frontend → voice-service przez proxy (`/api/voice/*`) | przeglądarka | brak (klucz dokłada backend) | [4](#4-proxy-frontend--voice-service-apivoice) |

Zasady wspólne:

- Przeglądarka rozmawia **tylko** z backendem, zawsze przez ścieżkę względną `/api/...`. Vite przekazuje ją na `http://localhost:8000`
  zarówno w `npm run dev`, jak i w `npm run preview` (`frontend/vite.config.ts`). Dlatego CORS nie jest potrzebny w żadnym serwisie.
- Frontend **nigdy** nie woła voice-service bezpośrednio, bo klucz API trafiłby do kodu JS.
- Ciało błędu to zawsze JSON `{"detail": ...}` (format FastAPI).
- Nagrania narracji gry (MP3) i grafiki **nie** idą przez API: to pliki statyczne frontendu (sekcja [5](#5-pliki-statyczne-frontendu)).

Porty domyślne: frontend dev `5173`, preview `4173`, backend `8000` (`API_PORT` w `backend/.env`),
voice-service `8001`, PostgreSQL `5432`.

---

## 2. Frontend → backend: historie

Backend odczytuje historie z PostgreSQL. Frontend pobiera wybraną historię **raz** i wykonuje wszystkie przejścia lokalnie;
wybory gracza nie są wysyłane do serwera. Nie ma zapisu ani sesji.

### `GET /api/health`

Czy API działa. **Nie** sprawdza bazy (healthcheck kontenera).

```json
{ "status": "ok" }
```

### `GET /api/stories`

Lista historii bez grafu scen. Pusta lista (`[]`) przed pierwszym importem.

```json
[
  {
    "id": "mostek-czarownic",
    "title": "Mostek Czarownic",
    "location": { "name": "kościół św. Marii Magdaleny", "center": [51.109531, 17.035053] },
    "intro": {
      "title": "…",
      "paragraphs": [
        [{ "if": { "widok": ["zachod"] }, "text": "…", "audio_url": "/audio/mostek-czarownic/intro-1-zachod.mp3" }, "…"]
      ]
    }
  }
]
```

### `GET /api/stories/{id}`

Pełna historia (model `Story` z `backend/app/models.py`). JSON jest zwracany prosto z bazy, bez przetwarzania;
został zwalidowany przy imporcie.

Najważniejsze pola (pełny opis: `terminal-game/docs/FORMAT_HISTORII.md` i `CLAUDE.md`, sekcja „Kontrakt danych”):

```text
Story: id, title, location, stops{}, route?, streetview?, test_points?, demo_start?,
       state{pole: [wartości]}, intro{title, paragraphs}, start, scenes{id: Scene},
       ending_by[], endings{klucz: Ending}, finale{act?, paragraphs}, reveal{title, paragraphs},
       ranks[{min, title, text}], heritage: Text, look_up: Text
Location: name, center[lat, lon], unlock_radius_m, default_view, viewpoints[{id, label, lat, lon, radius_m}]
Stop:     label, lat, lon, radius_m, walk, arrive
Scene:    title, scene: Paragraphs, options[2..3], fact, act?, before?, keypoint?, art?, bg?
Option:   text: Text, legend: bool, set{pole: wartość}, next: id sceny | null, result: Paragraphs
Ending:   title, paragraphs: Paragraphs, bg?
Text = napis | {if?: {pole: [wartości]}, text, audio_url?, chars?: {left?, right?}} | [warianty]
Paragraphs = [Text]
```

Logika po stronie frontendu:

- **Tekst z wariantami:** wygrywa pierwszy wariant, którego `if` pasuje do stanu (każde wymienione pole ma jedną z wartości);
  brak `if` pasuje zawsze; gdy nic nie pasuje, akapit się pomija.
- **Stan:** słownik pól z `state`. Wybór opcji zapisuje `set`. Pole `widok` ustawia frontend z GPS
  (id punktu widokowego albo `location.default_view`).
- **Koniec:** opcja z `next: null` kończy grę; zakończenie to `endings[ending_by.map(p => stan[p]).join("|")]`.
- **Wynik i ranga:** wynik = liczba wybranych opcji z `legend: true`; ranga = najwyższa z `min <= wynik`.
- **Przystanki:** scena z `before` czeka, aż gracz dojdzie do przystanku `stops[before]`.
- Pola zaczynające się od `_` to notatki autora; walidator i import je pomijają, frontend może je ignorować.

### Błędy

| Kod | Endpoint | Kiedy | `detail` |
|---|---|---|---|
| `404` | `/api/stories/{id}` | nieznane `id` | `"Nie ma takiej historii."` |
| `503` | `/api/stories`, `/api/stories/{id}` | baza niedostępna lub brak `DATABASE_URL` | `"Baza danych jest niedostępna."` |
| `502`/`504` lub błąd sieci | wszystkie | backend nie działa (zwraca proxy Vite albo `fetch` rzuca wyjątek) | brak lub HTML |

Frontend (`frontend/src/App.tsx`) każde niepowodzenie zamienia w ekran błędu. Nie zakładaj, że ciało błędu z proxy Vite jest JSON-em.

### Przykład (React)

```ts
const res = await fetch(`/api/stories/${id}`)
if (!res.ok) throw new Error(res.status === 404 ? 'Nie ma takiej historii.' : 'Nie udało się pobrać historii.')
const story: Story = await res.json()
```

### Konfiguracja i uruchomienie

`backend/.env` (kopia `.env.example`): `DATABASE_URL` dla uruchomienia przez uv; w Dockerze Compose ustawia go sam.
Treść trafia do bazy importem `uv run --env-file .env python -m app.import_story` (szczegóły: `backend/README.md`).

---

## 3. Backend → voice-service

voice-service (`voice-service/`) syntetyzuje mowę po polsku z klonowaniem głosu. W projekcie woła go **tylko backend**
(`backend/app/voice.py`); serwis powinien być dostępny wyłącznie w sieci wewnętrznej.

### Konfiguracja po stronie backendu

| Zmienna (`backend/.env`) | Przykład | Opis |
|---|---|---|
| `VOICE_SERVICE_URL` | `http://localhost:8001` | adres voice-service przy uruchomieniu przez uv |
| `VOICE_API_KEY` | `vs_...` | klucz z `uv run python genkey.py create backend` (w `voice-service/`, wypisywany raz) |

W Dockerze (`backend/docker-compose.yaml`) adres jest ustawiony na `http://host.docker.internal:8001`, bo voice-service
działa na hoście; `VOICE_API_KEY` jest brany z `.env`. Brak którejkolwiek zmiennej nie blokuje startu API:
endpointy `/api/voice/*` zwracają wtedy `503`, a historie działają normalnie.

Start voice-service: `uv run uvicorn app:app --host 0.0.0.0 --port 8001` w `voice-service/` (na Macu z `PYTORCH_ENABLE_MPS_FALLBACK=1`).
Serwis nie wystartuje bez co najmniej jednego klucza.

### Autoryzacja

Każdy endpoint poza `GET /health` wymaga nagłówka `X-API-Key: vs_...`. Brak lub zły klucz → `401`.
Odwołanie klucza (`genkey.py revoke`) działa od razu, bez restartu.

### Endpointy

| Metoda i ścieżka | Klucz | Ciało | Odpowiedź `200` |
|---|---|---|---|
| `GET /health` | nie | — | `{"status": "ok", "device": "cuda" \| "mps" \| "cpu"}` |
| `GET /voices` | tak | — | `{"voices": ["adrian", "kristina"]}` |
| `GET /characters` | tak | — | `{"characters": ["neutral", "starzec", "wiedzma"]}` |
| `POST /tts` | tak | `{voice, character?, text}` | `audio/wav` |
| `POST /tts/script` | tak | `{script}` | `audio/wav` |

**`POST /tts`** — jedna kwestia:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `voice` | string | tak | identyfikator głosu z `/voices` |
| `character` | string | nie (`neutral`) | identyfikator postaci z `/characters` |
| `text` | string | tak | 1–1000 znaków |

**`POST /tts/script`** — wiele kwestii w jednym nagraniu:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `script` | string | tak | 1–3000 znaków; każda niepusta linia `[Głos, postać] Kwestia`, kwestia do 1000 znaków |

Linie są generowane po kolei i sklejane z pauzą 0,5 s.

**Identyfikatory** głosów i postaci są normalizowane: wielkość liter i polskie znaki nie mają znaczenia (`Wiedźma` = `wiedzma`).
Każdy głos łączy się z każdą postacią.

### Format audio

`Content-Type: audio/wav`, WAV PCM 16-bit, mono, 24 kHz (ok. 48 KB na sekundę). Nagłówek
`Content-Disposition: attachment; filename="tts.wav"` można zignorować. Generacja nie jest deterministyczna.

### Błędy voice-service

| Kod | Kiedy | `detail` |
|---|---|---|
| `401` | brak lub zły `X-API-Key` | napis |
| `404` | nieznany głos lub postać | napis z listą dostępnych wartości |
| `422` | błąd walidacji pól | **lista obiektów** (format FastAPI) |
| `422` | zły format skryptu, za długa linia skryptu | **napis**, np. `"Linia 1: oczekiwano formatu '[Głos, postać] Kwestia'."` |
| `500` | błąd modelu lub serwera | traktuj jako niepowodzenie; można ponowić |

### Wydajność

- Generacja jest wolna: na CPU ok. 10× czasu nagrania (6,8 s audio ≈ 66 s). Na GPU/MPS szybciej.
- Serwis generuje **jedną kwestię naraz**; równoległe zapytania czekają w kolejce.
- Powtórzone zapytanie (ten sam głos, postać i tekst) wraca z cache dyskowego w ułamku sekundy.
- Backend czeka na odpowiedź maksymalnie **180 s** (`TIMEOUT_S` w `backend/app/voice.py`).

### Przykład (curl, bezpośrednio do voice-service)

```bash
curl -s -X POST http://localhost:8001/tts \
  -H "X-API-Key: $VOICE_API_KEY" -H "Content-Type: application/json" \
  -d '{"voice":"adrian","character":"starzec","text":"Siadajcie bliżej, dzieci."}' \
  -o tts.wav
```

Więcej szczegółów (dodawanie głosów, cache, narzędzia): `voice-service/README.md` i `voice-service/API.md`.

---

## 4. Proxy frontend → voice-service (`/api/voice/*`)

Backend wystawia lustrzane endpointy voice-service pod `/api/voice/`. Przeglądarka woła je bez klucza;
backend dokłada `X-API-Key` i przekazuje odpowiedź. Gra v0 z nich **nie korzysta** (narracja to gotowe MP3
z sekcji 5); to furtka na dynamiczną syntezę.

### Mapowanie

| Frontend woła (backend :8000) | Backend przekazuje do (voice-service :8001) |
|---|---|
| `GET /api/voice/health` | `GET /health` |
| `GET /api/voice/voices` | `GET /voices` |
| `GET /api/voice/characters` | `GET /characters` |
| `POST /api/voice/tts` | `POST /tts` |
| `POST /api/voice/tts/script` | `POST /tts/script` |

Ciała żądań i odpowiedzi `200` są **identyczne** jak w sekcji 3 (`audio/wav` dla syntezy, JSON dla list i health).
Backend sprawdza te same pola i limity (`text` 1–1000, `script` 1–3000 znaków) przed wysłaniem,
więc złe dane dostają `422` od razu, bez czekania na serwis.

### Błędy proxy

| Kod | Źródło | Kiedy | `detail` |
|---|---|---|---|
| `404` | voice-service, bez zmian | nieznany głos lub postać | napis |
| `422` | backend | złe pola (brak, pusty lub za długi tekst) | lista obiektów |
| `422` | voice-service, bez zmian | zły format skryptu, za długa linia | napis |
| `500` | voice-service, bez zmian | błąd modelu | zależy |
| `502` | backend | voice-service odrzucił klucz backendu (`401`) | `"Backend ma nieprawidłowy klucz voice-service."` |
| `503` | backend | brak `VOICE_SERVICE_URL`/`VOICE_API_KEY` albo serwis nie odpowiada | `"Serwis głosu jest niedostępny."` |
| `504` | backend | brak odpowiedzi w ciągu 180 s | `"Serwis głosu nie odpowiedział na czas."` |

Kod `401` nigdy nie dociera do przeglądarki: problem z kluczem dotyczy konfiguracji backendu, nie gracza.
Przy `422` `detail` ma dwa kształty, więc sprawdzaj `typeof detail === "string"`.

### Przykład (React)

```ts
async function speak(voice: string, character: string, text: string, signal?: AbortSignal): Promise<HTMLAudioElement> {
  const res = await fetch('/api/voice/tts', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ voice, character, text }),
    signal,
  })
  if (!res.ok) {
    const detail = await res.json().then((b) => b.detail, () => null)
    throw new Error(typeof detail === 'string' ? detail : 'Nie udało się wygenerować nagrania.')
  }
  const url = URL.createObjectURL(await res.blob())
  const audio = new Audio(url)
  audio.onended = () => URL.revokeObjectURL(url)
  await audio.play()
  return audio
}
```

Na co uważać:

- **Czas:** odpowiedź może przyjść po kilkudziesięciu sekundach. Pokaż stan ładowania i pozwól ponowić.
- **Autoplay:** pierwsze `play()` musi nastąpić po geście użytkownika (kliknięcie).
- **Przerwanie:** przy zmianie sceny zatrzymaj stare `Audio` i anuluj zapytanie (`AbortController`).
  Anulowanie po stronie przeglądarki nie przerywa generacji w voice-service.
- **Kolejka:** nie wysyłaj wielu zapytań naraz; serwis i tak przetwarza je po kolei.
- **Pamięć:** `URL.revokeObjectURL` po odtworzeniu.
- **Service worker** (gdy powstanie): nie cache'uj `/api`, także `/api/voice`; zasada z `CLAUDE.md` to „cache powłoki, nie API”.

### Bezpieczeństwo

Proxy pozwala każdemu, kto ma dostęp do backendu, zlecić syntezę **dowolnego** tekstu dowolnym głosem
i zablokować serwis długą kolejką. Na demo w sieci lokalnej to akceptowalne; przed publicznym wystawieniem
trzeba ograniczyć dostęp (np. tylko teksty z treści gry, limit zapytań) albo wyłączyć proxy (pusty `VOICE_API_KEY`).

---

## 5. Pliki statyczne frontendu

Nie są częścią API backendu; serwuje je Vite z `frontend/public/` (w dev, preview i po buildzie).

| Ścieżka | Zawartość | Skąd adres |
|---|---|---|
| `/audio/<id historii>/<plik>.mp3` | nagranie jednego akapitu lub wariantu | `audio_url` w treści historii |
| `/audio/<id historii>/<plik>.json` | opcjonalne znaczniki czasu słów `{"words": [{text, start, end}]}` (karaoke) | ta sama nazwa co MP3; brak = czas rozkładany proporcjonalnie |
| `/art/<id historii>/<plik>.png` | tła i postacie | `bg`, `chars.left`, `chars.right` w treści historii |

Brak pliku to zwykłe `404` serwera statycznego; przy błędzie nagrania odtwarzacz narracji oznacza akapit jako bez dźwięku, a tekst zostaje.
Przypisanie głosów do akapitów: `voice-service/NARRACJA.md`.

---

## 6. Zmiany kontraktu

- Kontrakt historii: modele w `backend/app/models.py` (źródło prawdy), typy we `frontend/src/game/types.ts`, walidator i treść w `content/`.
- Kontrakt voice-service: `voice-service/app.py`; limity są powtórzone w `backend/app/main.py` (`TtsRequest`, `ScriptRequest`).

Zmiana pól, kodów błędów, formatu audio lub limitów wymaga uzgodnienia ze wszystkimi modułami, które z nich korzystają,
oraz aktualizacji tego pliku.
