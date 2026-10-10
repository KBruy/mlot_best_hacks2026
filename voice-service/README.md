# voice-service

Wewnętrzny serwis TTS z klonowaniem głosu (Chatterbox Multilingual, język polski). Osobny serwis gry.

## Start

```
uv sync
uv run python genkey.py create gra          # klucz API, wypisany JEDEN raz
uv run uvicorn app:app --host 0.0.0.0 --port 8001
```

Model (~3 GB) pobiera się z Hugging Face przy pierwszym starcie. Urządzenie jest wykrywane samo (CUDA / MPS / CPU).
Na Macu: `PYTORCH_ENABLE_MPS_FALLBACK=1 uv run uvicorn ...`. Dokumentacja API: `/docs`.

## Głosy i postacie

- Głos: `voices/<głos>_neutral.wav` (10–20 s czystego nagrania). Nagrania są poza gitem.
- Maniera: opcjonalny plik `voices/<głos>_<postać>.wav` zastępuje próbkę neutralną (lepszy efekt niż same parametry).
- Postacie i ich parametry: `characters.yaml`. Nowa postać to nowy wpis, bez zmian w kodzie.

## Jak dodać nowy głos

Nowy głos to jedno nagranie. Kod i konfiguracja się nie zmieniają, a serwis nie wymaga restartu.

1. **Nagraj próbkę** (patrz niżej: wymagania i tekst do przeczytania).
2. **Zapisz ją jako** `voices/<głos>_neutral.wav`, np. `voices/kristina_neutral.wav`.
   - Nazwa głosu: **małe litery, bez polskich znaków i bez podkreślników** (`kristina`, `jan`, nie `Kristina` ani `jan_kowalski`).
     To ona jest identyfikatorem w API. Plik `Kristina_neutral.wav` nie zostanie znaleziony.
   - Plik musi być `.wav`. Z innego formatu: `ffmpeg -i nagranie.m4a -ac 1 -ar 24000 voices/kristina_neutral.wav`.
3. **Sprawdź**: `GET /voices` pokazuje nowy głos od razu (bez restartu), a `POST /tts` z `"voice":"kristina"` generuje jego mową.
4. **Opcjonalnie nagraj maniery** dla wybranych postaci: `voices/kristina_starzec.wav`, `voices/kristina_wiedzma.wav`.
   Dla pary (głos, postać) serwis używa takiego pliku zamiast neutralnego, a gdy go nie ma, korzysta z neutralnego.
   W teście jakości osobne nagranie w manierze wychodziło lepiej niż same parametry postaci.

Nagrania są poza gitem (`voices/` jest w `.gitignore`), więc na innym komputerze (np. Macu) trzeba je skopiować ręcznie.
Po podmianie pliku nagrania cache tego głosu unieważnia się sam.

### Wymagania dotyczące nagrania

- 10–20 s czystej mowy, **jedno ciągłe podejście**, bez cięć.
- Cichy pokój bez pogłosu, mikrofon ok. 15 cm od ust, z boku (żeby nie łapał „p" i „b"). Bez muzyki i szumu w tle.
- Mów naturalnie, jak do kogoś, a nie jak lektor.
- **Zgoda osoby** na sklonowanie jej głosu. Wewnętrznie to proste, ale warto mieć to zapisane.

### Teksty do przeczytania

Neutralny (`<głos>_neutral.wav`, ok. 20 s):

> Dawno temu, we Wrocławiu, nad brzegiem Odry stała stara kamienica. Mieszkańcy opowiadali, że po zmroku ktoś chodzi po schodach, choć drzwi są zamknięte na klucz. Jedni się śmiali, inni zapalali świece i szeptali modlitwy. Ja wiem tylko tyle, że rano zawsze pachniało dymem.

Starzec (`<głos>_starzec.wav`): wolno, nisko, zmęczonym, lekko ochrypłym głosem, z pauzami:

> Siadajcie bliżej, dzieci, bo ta historia jest długa, a mój głos już nie ten, co kiedyś. Pamiętam czasy, gdy rzeka płynęła szybciej, a wiatr niósł szepty z całego miasta.

Wiedźma (`<głos>_wiedzma.wav`): szybko, głośno, z emocją i śmiechem:

> Ha, trzymajcie się czapek, głupcy, bo lecę nad waszymi dachami! Miotła skrzypi, wiatr gwiżdże w uszach, a wy tam na dole drżycie ze strachu!

Nowa postać (a nie głos) to wpis w `characters.yaml` i **restart** serwisu. Plik jest czytany tylko przy starcie.

## Jak dodać nową postać

Postać to styl mówienia (ekspresja i tempo). Nie zmienia barwy głosu. Jest to wpis w `characters.yaml`:

```yaml
rycerz:              # klucz: małe litery, bez polskich znaków
  exaggeration: 0.5
  cfg_weight: 0.4
```

1. Dodaj wpis i **zrestartuj serwis** (plik jest czytany tylko przy starcie). `GET /characters` pokaże nową postać.
2. Każdy istniejący głos może jej od razu używać. Bez osobnej próbki serwis używa nagrania neutralnego z parametrami postaci.
3. **Opcjonalnie** nagraj próbkę w manierze: `voices/<głos>_rycerz.wav`. Zwykle brzmi lepiej niż same parametry.
4. Parametry dobieraj na słuch, zmieniając je o 0,1–0,2 (testowane było `exaggeration` 0,3–0,8 i `cfg_weight` 0,3–0,5; skrajne wartości nie były sprawdzane).
   Znaczenie parametrów i dozwolone nazwy opisuje komentarz na górze `characters.yaml`.
   Zostaw `repetition_penalty` na ok. 2,5, bo poniżej ok. 2 audio jest ucinane.

Czego postać **nie** zrobi: nie zmieni wysokości ani barwy głosu (np. dziecko lub staruszka z głosu dorosłego mężczyzny)
i nie doda efektów (pogłos, pitch). Taka postać wymaga nagrania w danej manierze albo osobnego głosu innej osoby.

## API (nagłówek `X-API-Key`; wyjątek: `GET /health`)

| Metoda | Ścieżka                  | Opis                                                                                      |
| ------ | ------------------------ | ----------------------------------------------------------------------------------------- |
| POST   | `/tts`                   | `{"voice":"adrian","character":"starzec","text":"..."}` → `audio/wav`                     |
| POST   | `/tts/script`            | `{"script":"[Adrian, starzec] Kwestia\n[Kristina, wiedźma] Kwestia"}` → jeden `audio/wav` |
| GET    | `/voices`, `/characters` | dostępne identyfikatory                                                                   |

Identyfikatory są normalizowane (`Wiedźma` = `wiedzma`). Błędy: 401 (klucz), 404 (nieznany głos lub postać), 422 (zły skrypt lub tekst).
Limity: 1000 znaków na kwestię, 3000 na skrypt. Dłuższe kwestie są dzielone na zdania. Wyniki są cache'owane w `cache/`
(klucz: głos, postać, parametry, tekst, próbka), więc powtórzona kwestia wraca od razu.

Pełny kontrakt dla backendu i frontendu (błędy, format audio, czasy, przykłady): [`API.md`](API.md).

## Klucze

```
uv run python genkey.py create <nazwa> | list | revoke <nazwa>
```

Plik `api_keys.json` trzyma tylko skróty SHA-256. Odwołanie klucza działa bez restartu.

## Narzędzia i testy

- `spike.py`, `tune.py`: odsłuch jakości i strojenie parametrów (wyniki w `outputs/`).
- `uv run pytest`: testy parsera, dzielenia tekstu i kluczy (bez modelu).
- Szum na końcu nagrań (wymuszony EOS) usuwa `audio.trim_tail`.
