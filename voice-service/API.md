# Kontrakt API: voice-service

Dokument dla backendu gry i frontendu (React). Schemat techniczny (typy pól) jest zawsze aktualny
w Swaggerze: `GET /docs` i `GET /openapi.json`. Ten plik opisuje to, czego schemat nie mówi:
kto z kim rozmawia, jakie błędy się zdarzają, ile to trwa i jak z tego korzystać.

## 1. Kto z kim rozmawia

```
React (przeglądarka) ──► backend gry (/api/...) ──► voice-service (:8001)
                          trzyma klucz API            nagłówek X-API-Key
```

- **React nigdy nie woła voice-service bezpośrednio.** Klucz API trafiłby do kodu JS i byłby dostępny dla każdego gracza.
- Klucz trzyma backend gry (np. w `.env`) i dokłada go do każdego zapytania do voice-service.
- Przy takim układzie CORS w voice-service **nie jest potrzebny** (przeglądarka rozmawia tylko z backendem gry).
- voice-service powinien być dostępny tylko w sieci wewnętrznej.

## 2. Autoryzacja

Każdy endpoint poza `GET /health` wymaga nagłówka:

```
X-API-Key: vs_...
```

Klucz tworzy się narzędziem `uv run python genkey.py create <nazwa>` (wypisywany jest jeden raz). Brak lub zły klucz → `401`.
Odwołanie klucza (`genkey.py revoke`) działa od razu, bez restartu serwisu.

## 3. Identyfikatory

- **Głos** (`voice`): osoba, której głos jest sklonowany, np. `adrian`, `kristina`. Lista: `GET /voices`.
- **Postać** (`character`): styl wypowiedzi, np. `neutral`, `starzec`, `wiedzma`. Lista: `GET /characters`.
- Identyfikatory są **normalizowane**: wielkość liter i polskie znaki nie mają znaczenia (`Wiedźma` = `wiedzma`).
  Odpowiedzi `/voices` i `/characters` zawsze zwracają formę znormalizowaną. Do kodu zapisuj ją.
- Nowe głosy i postacie dodaje się po stronie serwisu (instrukcja w [README](README.md#jak-dodać-nowy-głos)). Klient tylko odczytuje `/voices` i `/characters`, więc dodanie głosu nie zmienia kontraktu.
- Każdy głos można połączyć z każdą postacią. Jeśli dla pary istnieje nagranie w danej manierze, jest użyte,
  w przeciwnym razie serwis używa próbki neutralnej i zmienia tylko parametry. Dla klienta różnicy w API nie ma.

## 4. Endpointy

### `GET /health` (bez klucza)

```json
{ "status": "ok", "device": "mps" }
```

`device`: `cuda`, `mps` lub `cpu`. Nadaje się do sprawdzania, czy serwis żyje (model jest wtedy już załadowany).

### `GET /voices`, `GET /characters`

```json
{ "voices": ["adrian", "kristina"] }
{ "characters": ["neutral", "starzec", "wiedzma"] }
```

### `POST /tts`: jedna kwestia

Żądanie (`Content-Type: application/json`):

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `voice` | string | tak | identyfikator głosu |
| `character` | string | nie (domyślnie `neutral`) | identyfikator postaci |
| `text` | string | tak | 1–1000 znaków |

```json
{ "voice": "adrian", "character": "starzec", "text": "Siadajcie bliżej, dzieci." }
```

Odpowiedź `200`: **binarny plik audio**, nie JSON (patrz sekcja 5).

### `POST /tts/script`: wiele kwestii w jednym nagraniu

Żądanie:

| Pole | Typ | Wymagane | Opis |
|---|---|---|---|
| `script` | string | tak | 1–3000 znaków, jedna lub więcej linii |

Każda niepusta linia ma format `[Głos, postać] Kwestia`:

```json
{ "script": "[Adrian, starzec] Siadajcie bliżej, dzieci.\n[Kristina, wiedźma] Ha, trzymajcie się czapek!" }
```

Linie są generowane po kolei i sklejane w **jedno** nagranie z pauzą 0,5 s między nimi. Kwestia w linii: do 1000 znaków.
Odpowiedź `200`: binarny plik audio, jak w `/tts`.

## 5. Format audio

- `Content-Type: audio/wav`, WAV **PCM 16-bit, mono, 24 kHz**. Ok. 48 KB na sekundę nagrania.
- Odpowiedź ma `Content-Disposition: attachment; filename="tts.wav"`. To tylko wygoda dla Swaggera, klient może to zignorować.
- Dłuższe kwestie są dzielone na zdania i sklejane (pauza 0,25 s). Klient dostaje zawsze jeden plik.
- Nagranie ma przycięty szum na końcu. Nie zakładaj stałej długości ani identycznych bajtów dla tego samego tekstu
  po wyczyszczeniu cache (generacja nie jest deterministyczna).

## 6. Błędy

| Kod | Kiedy | `detail` |
|---|---|---|
| `401` | brak lub zły `X-API-Key` | napis |
| `404` | nieznany głos lub postać | napis z listą dostępnych wartości |
| `422` | błąd walidacji pól (brak pola, pusty lub za długi tekst) | **lista obiektów** (format FastAPI) |
| `422` | zły format skryptu, za długa linia w skrypcie | **napis**, np. `Linia 1: oczekiwano formatu '[Głos, postać] Kwestia'.` |
| `500` | błąd modelu lub serwera | zależy; traktuj jako niepowodzenie, można ponowić |

Ciało błędu to zawsze `{"detail": ...}`. Uwaga: przy `422` `detail` ma dwa różne kształty (lista lub napis),
więc klient nie może zakładać jednego typu. Wystarczy sprawdzić `typeof detail === "string"`.

```json
{ "detail": "Nieznana postać 'ork'. Dostępne: neutral, starzec, wiedzma." }
{ "detail": [ { "type": "string_too_long", "loc": ["body", "text"], "msg": "String should have at most 1000 characters" } ] }
```

## 7. Czas odpowiedzi i obciążenie

- Generacja jest **wolna** w porównaniu z typowym API. Na CPU Windowsa zmierzyliśmy ok. **10× czasu rzeczywistego**
  (6,8 s audio ≈ 66 s). Na Macu M5 jest wyraźnie szybciej, ale liczb jeszcze nie mamy; zmierz przed ustawieniem timeoutów.
- Serwis generuje **jedną kwestię naraz**. Równoległe zapytania ustawiają się w kolejce, więc nie wysyłaj ich lawinowo.
- Powtórzone zapytanie (ten sam głos, postać, tekst i próbka) wraca z cache dyskowego w ułamku sekundy.
- **Zalecenia dla backendu:** timeout po stronie klienta HTTP znacznie dłuższy niż zwykle (min. 180 s do czasu pomiaru na docelowym sprzęcie),
  generowanie z wyprzedzeniem (np. gdy gracz czyta poprzednią scenę) i własny cache gotowych plików po `(voice, character, text)`.

## 8. Przykłady

### curl

```bash
curl -s -X POST http://localhost:8001/tts \
  -H "X-API-Key: $VOICE_API_KEY" -H "Content-Type: application/json" \
  -d '{"voice":"adrian","character":"starzec","text":"Siadajcie bliżej, dzieci."}' \
  -o tts.wav
```

### Backend gry (FastAPI + httpx): proxy, który ukrywa klucz

```python
VOICE_URL = os.environ["VOICE_SERVICE_URL"]     # np. http://localhost:8001
VOICE_KEY = os.environ["VOICE_API_KEY"]

@app.post("/api/tts")
async def tts(body: dict):
    async with httpx.AsyncClient(timeout=180) as client:
        r = await client.post(f"{VOICE_URL}/tts", json=body, headers={"X-API-Key": VOICE_KEY})
    if r.status_code != 200:
        return Response(r.content, r.status_code, media_type="application/json")
    return Response(r.content, media_type="audio/wav")
```

Backend powinien ograniczyć, co przekazuje (np. tylko `voice`, `character`, `text` z własnej treści gry),
żeby gracz nie mógł zlecać dowolnych tekstów.

### React: pobranie i odtworzenie

```ts
async function speak(voice: string, character: string, text: string): Promise<void> {
  const res = await fetch("/api/tts", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ voice, character, text }),
  });
  if (!res.ok) {
    const { detail } = await res.json();
    throw new Error(typeof detail === "string" ? detail : "Nieprawidłowe dane żądania");
  }
  const url = URL.createObjectURL(await res.blob());
  const audio = new Audio(url);
  audio.onended = () => URL.revokeObjectURL(url);
  await audio.play();
}
```

Na co uważać po stronie Reacta:
- **Autoplay:** pierwsze `play()` musi nastąpić po geście użytkownika (kliknięcie „Dalej"). Potem odtwarzanie automatyczne zwykle działa.
- **Stan ładowania:** odpowiedź może przyjść po kilku sekundach lub dłużej. Pokaż wskaźnik i obsłuż błąd z możliwością ponowienia.
- **Zwalnianie pamięci:** `URL.revokeObjectURL` po zakończeniu odtwarzania.
- **Przerwanie:** przy zmianie sceny zatrzymaj stare `Audio` i anuluj zapytanie (`AbortController`), żeby nie odtworzyć kwestii z poprzedniej sceny.

## 9. Zmiany kontraktu

Zmiana pól, kodów błędów, formatu audio lub limitów wymaga uzgodnienia z backendem i frontendem oraz aktualizacji tego pliku
(zasada z `CLAUDE.md`: zmiana kontraktu wymaga skoordynowania wszystkich używających go modułów).
