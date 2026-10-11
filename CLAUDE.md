# CLAUDE.md

## Cel i twardy limit

Budujemy demo polskojęzycznej PWA: interaktywny spacer z legendą wrocławską w miejscu jej akcji (GPS), z decyzjami fabularnymi. Zespół: 4 osoby. **V0 ma powstać w maksymalnie 3–4 godziny**, nie w 24 godziny. Optymalizuj pod kompletny przepływ i minimalną liczbę elementów.

Backend (`backend/`) jest już zaimplementowany; jego szczegóły opisuje `backend/README.md`. Szczegółowy zakres i taski są w `SCOPE_V0.md` oraz `TASKI_V0.md`, jeśli skopiowano je razem z nim. Przed pracą sprawdź rzeczywistą strukturę i istniejące instrukcje.

## Zakres v0

- Jedna legenda: „Mostek Czarownic” (`content/legenda-czarownica.json`), bez wyboru postaci; gracz jest najpierw panną, potem młodą czarownicą.
- Dokładnie 6 decyzji na każdej ścieżce, 2–3 opisowe opcje na decyzję, zakończenia wybierane stanem (`ending_by`).
- Każda opcja ma własny skutek (`result`). Po wyborze pokaż go, potem „Dalej” prowadzi do sceny `next` albo do zakończenia.
- Gałęzie mogą się łączyć. Teksty mogą zależeć od wcześniejszych wyborów i punktu widokowego (warianty `if`). Wynik to liczba wyborów zgodnych z legendą, pokazywany z rangą dopiero na końcu, razem z faktami z legendy.
- Lokalizacja: gra odblokowuje się w pobliżu miejsca legendy, punkt widokowy wybiera wariant wstępu, sceny z `before` czekają na dojście do przystanku. Trasa i Street View są opcjonalne.
- Spacer i czytanie do 10 minut. Zmierz pełne przejście; krótsze demo można przekazać w terminie, ale wyraźnie oznacz niezrealizowany czas.
- UI mobilne: start/wstęp, dojście do miejsca, scena, skutek, zakończenie z finałem i rangą, nowa gra, loading/błąd/ponowienie.
- PWA: manifest, lokalne ikony i service worker cache’ujący powłokę. Pełne offline i trwały zapis nie należą do v0.

**Zero AI w aplikacji i tworzeniu treści.** Nie dodawaj SDK modeli, wywołań LLM, embeddingów ani generowanych ilustracji. Finalne teksty i graf dostarcza zespół ręcznie. Nie generuj finalnej narracji; techniczne fixture mogą zawierać neutralne etykiety typu „Scena 1”.

Poza zakresem: pozostałe dwie legendy, osobne pełne kampanie postaci, konta, zapis/wznowienie, synchronizacja, pełny offline, walka, ekwipunek, statystyki, losowość, panel autora, multiplayer, analityka, CI/CD i nowa infrastruktura hostingowa.

## Technologia i prostota

- Vite + React + TypeScript, zwykły CSS, stan React. Bez routera, jeśli nie jest potrzebny do istniejącego kodu.
- FastAPI, Pydantic, PostgreSQL w Dockerze.
- `backend/` i `frontend/` to osobne podserwisy. Backend ma własny `docker-compose.yaml` (API + baza), `.env.example` i `README.md`; frontend uruchamiany lokalnie. Nie konteneryzuj frontendu tylko dla symetrii.
- Konfiguracja przez pliki `.env` (kopie `.env.example`), nie przez ręcznie eksportowane zmienne środowiskowe.
- Baza może trzymać wiele historii: tabela `stories(id TEXT PRIMARY KEY, payload JSONB NOT NULL)`, jeden wiersz na historię.
- API: `GET /api/stories` (lista `{id, title, location: {name, center}, intro: {title, paragraphs}}`) i `GET /api/stories/{id}` (pełna historia, 404 dla nieznanego id). Niedostępna baza: kontrolowany 503. Kontrakt odpowiedzi opisuje Swagger (`/docs`).
- Import (`python -m app.import_story`) bierze `content/*.json` (jeden plik = jedna historia), waliduje je i robi upsert po `id` w jednej transakcji. Bez ORM i frameworka migracji.
- Frontend pobiera wybraną historię raz i wykonuje wszystkie przejścia lokalnie. Nie wysyłaj wyborów do serwera.
- Proxy `/api` musi działać zarówno w development, jak i podglądzie produkcyjnego buildu. Nie dodawaj niepotrzebnej konfiguracji CORS.

Struktura:

```text
frontend/
backend/            # FastAPI, docker-compose.yaml, .env.example, tests/
content/*.json      # historie (jeden plik = jedna historia)
README.md
CLAUDE.md
```

Zachowuj zastane konwencje i lockfile. Nie twórz równoległego szkieletu. Nie dodawaj biblioteki, jeśli prosty kod wystarczy w tym zakresie.

## Kontrakt danych

Frontend, backend i autor treści używają jednego kontraktu. Źródłem prawdy są modele w `backend/app/models.py` (widoczne też w `/docs`); zmiana kontraktu wymaga koordynacji wszystkich modułów.

Format pochodzi z prototypu `terminal-game/` (pełny opis pól: `terminal-game/docs/FORMAT_HISTORII.md`), z dodanymi `id` i `title` dla bazy i API.

```text
Story: id, title, location, stops{}, route?, streetview?, test_points?, demo_start?,
       state{pole: [wartości]}, intro{title, paragraphs}, start, scenes{id: Scene},
       ending_by[], endings{klucz: Ending}, finale{act?, paragraphs}, reveal{title, paragraphs},
       ranks[{min, title, text}], heritage: Text, look_up: Text
Location: name, center[lat, lon], unlock_radius_m, default_view, viewpoints[{id, label, lat, lon, radius_m}]
Stop: label, lat, lon, radius_m, walk, arrive
Scene: title, scene: Paragraphs, options[2..3], fact, act?, before?, keypoint?, art?, bg?
Option: text: Text, legend: bool, set{pole: wartość}, next: id sceny | null, result: Paragraphs
Ending: title, paragraphs: Paragraphs, bg?
Text = napis | {if?: {pole: [wartości]}, text, audio_url?, chars?: {left?, right?}} | [warianty]   (wygrywa pierwszy pasujący, brak = akapit pominięty)
Paragraphs = [Text]
```

Stan gry to słownik pól z `state`; opcja zapisuje w nim `set`. Pole `widok` frontend ustawia z GPS (id punktu widokowego albo `location.default_view`). Opcja z `next: null` kończy grę: zakończenie to `endings["|".join(stan[p] for p in ending_by)]`. Wynik to liczba wybranych opcji z `legend: true`; ranga to najwyższa z `min <= wynik`. Scena z `before` wymaga dojścia do przystanku. Pola zaczynające się od `_` to notatki, pomijane przez walidator i import.

Walidator (`python -m app.validate`, ten sam przy imporcie) sprawdza wszystkie ścieżki: istniejące `start`, `next` i `before`; 2–3 opcje; warunki i `set` tylko z `state`; `audio_url` w ścieżce historii, jeden plik na jeden tekst, brak nagrań tekstów opcji; brak cykli i nieosiągalnych scen; dokładnie 6 decyzji na każdej ścieżce; każda ścieżka ustala pola `ending_by`, każda kombinacja ich wartości ma zakończenie i każde zakończenie jest osiągalne; jest ranga `min: 0`.

`audio_url` należy do pojedynczego akapitu albo wariantu: każdy czytany akapit (wstęp, scena, skutek, zakończenie, `finale`, `reveal`, `heritage`, `look_up`) i każdy jego wariant `if` ma osobne nagranie MP3 `/audio/<id historii>/<plik>.mp3`, serwowane statycznie przez frontend z `frontend/public/audio/`. Akapit bez warunku z nagraniem to wariant bez `if`: `{"text", "audio_url"}`. Teksty opcji nie są czytane. Jeden plik może służyć tylko identycznemu tekstowi. Obok MP3 może leżeć `<plik>.json` ze znacznikami czasu słów do karaoke (`{"words": [{text, start, end}]}`); bez niego front rozkłada czas nagrania proporcjonalnie na słowa. Przypisanie głosów i plików: `voice-service/NARRACJA.md` (Mostek Czarownic), `voice-service/NARRACJA-<id historii>.md` (pozostałe). Backend nie przechowuje plików audio.

Narracja jest zwykłym tekstem z akapitami; nie renderuj dowolnego HTML. Nie hardkoduj treści ani ID scen w komponentach. Warunki są tylko w formie `if` powyżej (bez wyrażeń i `eval`); nie rozbudowuj ich w ogólny język.

## Stan i UI

Stan gry: bieżąca scena, słownik pól stanu (`set` z wyborów i `widok` z GPS), liczba wykonanych decyzji, wynik (wybory z `legend: true`), wybrany skutek i jego cel. Wybór nalicza decyzję i wynik raz, a „Dalej” tylko zmienia scenę. Chroń przed podwójnym kliknięciem. Bez zgody na lokalizację albo daleko od miejsca pokaż zrozumiały komunikat; nie blokuj gry na stałe, gdy GPS jest niedokładny.

Bez localStorage i serwerowego zapisu. Odświeżenie resetuje rozgrywkę; poinformuj o tym na starcie. Nowa gra zaczyna od `start` z pustym stanem i zerowym wynikiem. Nie wprowadzaj wersjonowania sesji, bo sesji trwałych w v0 nie ma.

Minimum UI: 360 px bez poziomego przewijania, zawijanie długich opcji, czytelne akapity, duże przyciski, semantyczne elementy i widoczny fokus. Po zmianie sceny ustaw sensownie fokus. Użyj systemowych fontów, bez ilustracji i ozdobnych animacji wymagających dodatkowej pracy. Komunikaty po polsku.

## PWA i sieć

Cache’uj powłokę aplikacji, nie API. Po pobraniu historii gra działa w pamięci i nie potrzebuje sieci do następnych decyzji. Nie obiecuj gry offline po ponownym otwarciu ani wznowienia. Bez sieci powłoka ma wyświetlić zrozumiały komunikat i możliwość ponowienia pobrania.

Testuj service worker i instalację na produkcyjnym buildzie, przez localhost lub HTTPS. Bez gotowego hostingu HTTPS sprawdź instalację lokalnie na Chrome/desktop; nie poświęcaj limitu na budowę infrastruktury. Zwykły HTTP przez IP komputera w LAN nie jest podstawą odbioru PWA na telefonie. Zanotuj rzeczywiście sprawdzone środowisko.

## Praca w zespole

- A: komponenty, stan gry, integracja API.
- B: backend, baza, Compose, importer i walidator.
- C: własne teksty i finalny `content/legenda-czarownica.json` (`backend/tests/fixtures/legend.json` to neutralny fixture testów, poza importem).
- D: szkielet frontendu, neutralny fixture, konfiguracja PWA, osobny CSS, odbiór i README.

Nie nadpisuj pracy innych osób. Zmiana kontraktu wymaga skoordynowania wszystkich używających go modułów. Wybieraj jeden atomowy task i kończ jego kryterium akceptacji. Nie rozszerzaj zakresu „przy okazji”.

## Weryfikacja i zakończenie

Przeczytaj rzeczywiste skrypty przed uruchomieniem komend. Przy inicjalizacji udokumentuj start bazy/API, import treści, start frontendu, build i preview. Nie twierdź, że komenda istnieje lub test przeszedł, jeśli tego nie sprawdzono.

Minimalny odbiór:

1. Build frontendu i kontrola typów przechodzą.
2. Walidator akceptuje finalną historię; odrzuca przykłady z brakującym celem, cyklem, niepoprawną liczbą decyzji, złym warunkiem i brakującym zakończeniem.
3. Ponowny import nie duplikuje rekordu; API odczytuje treść z bazy.
4. Pełne przejście ma 6 decyzji; sprawdzone wszystkie drogi fazy 1, warianty tekstów, wszystkie zakończenia, ranga, nowa gra i szybkie dwukrotne kliknięcie.
5. Zmierzono czas czytania; autor sprawdził wszystkie opcje i konsekwencje.
6. Mobilny układ, klawiatura, instalacja PWA, zachowanie bez API i bez GPS/z odmową lokalizacji zostały sprawdzone i opisane.
7. README pozwala uruchomić demo i opisuje brak zapisu oraz ograniczenia offline.

Nie buduj frameworka E2E ani rozbudowanego CI dla tego demo. Backend ma testy pytest (`uv run pytest` w `backend/`, bez Dockera); utrzymuj je przy zmianach backendu. Walidator i ręczny odbiór krytycznej ścieżki są obowiązkowe.

Po 2 godzinach musi istnieć pełna pierwsza wersja tekstów. Po 3 godzinach nie dodawaj funkcji. Ostatnia godzina jest przeznaczona na błędy blokujące i przekazanie. Przy zagrożeniu terminu skracaj opisy i ozdobniki; nie ukrywaj niespełnionych wymagań. Nie wdrażaj na płatną infrastrukturę ani nie publikuj bez polecenia zespołu.
