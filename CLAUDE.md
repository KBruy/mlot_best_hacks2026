# CLAUDE.md

## Cel i twardy limit

Budujemy demo polskojęzycznej PWA: interaktywna adaptacja jednej legendy wrocławskiej, wybór postaci i decyzje fabularne. Zespół: 4 osoby. **V0 ma powstać w maksymalnie 3–4 godziny**, nie w 24 godziny. Optymalizuj pod kompletny przepływ i minimalną liczbę elementów.

To instrukcja dla przyszłego repozytorium, nie opis już istniejącej implementacji. Umieść ten plik w katalogu głównym. Szczegółowy zakres i taski są w `SCOPE_V0.md` oraz `TASKI_V0.md`, jeśli skopiowano je razem z nim. Przed pracą sprawdź rzeczywistą strukturę i istniejące instrukcje.

## Zakres v0

- Jedna legenda, dwie postaci, dokładnie 6 decyzji na przejście, po 2 opisowe opcje na decyzję i dwa zakończenia.
- Dwie różne sceny pierwszej decyzji zależne od postaci; etapy 2–6 wspólne. Łącznie 9 węzłów: 7 decyzyjnych i 2 finały.
- Każda opcja ma własny tekst konsekwencji. Po wyborze pokaż go, potem „Dalej” prowadzi do wskazanego węzła.
- Decyzje 1–5 mogą łączyć gałęzie w tym samym kolejnym węźle. Ostatnia decyzja wybiera finał. Bez punktacji i warunków opartych na wcześniejszych wyborach.
- Około 8 minut czytania i wyborów. Zmierz pełne przejście; cel 7–10 minut. Krótsze demo można przekazać w terminie, ale wyraźnie oznacz niezrealizowany czas narracji.
- UI mobilne: start/postaci, scena, konsekwencja, zakończenie, nowa gra, loading/błąd/ponowienie.
- PWA: manifest, lokalne ikony i service worker cache’ujący powłokę. Pełne offline i trwały zapis nie należą do v0.

**Zero AI w aplikacji i tworzeniu treści.** Nie dodawaj SDK modeli, wywołań LLM, embeddingów ani generowanych ilustracji. Finalne teksty i graf dostarcza zespół ręcznie. Nie generuj finalnej narracji; techniczne fixture mogą zawierać neutralne etykiety typu „Scena 1”.

Poza zakresem: pozostałe dwie legendy, osobne pełne kampanie postaci, konta, zapis/wznowienie, synchronizacja, pełny offline, walka, ekwipunek, statystyki, losowość, mapa/GPS, audio, panel autora, multiplayer, analityka, CI/CD i nowa infrastruktura hostingowa.

## Technologia i prostota

- Vite + React + TypeScript, zwykły CSS, stan React. Bez routera, jeśli nie jest potrzebny do istniejącego kodu.
- FastAPI, Pydantic, PostgreSQL w Dockerze.
- Compose dla API i bazy; frontend uruchamiany lokalnie. Nie konteneryzuj frontendu tylko dla symetrii.
- Jeden endpoint `GET /api/story`: pełna historia z PostgreSQL. Niedostępna baza/brak historii: kontrolowany 503.
- Jedna tabela `stories(id TEXT PRIMARY KEY, payload JSONB NOT NULL)`.
- Jeden skrypt tworzący tabelę i importujący `content/legend.json` przez upsert. Bez ORM i frameworka migracji, chyba że są już w używanym szablonie.
- Frontend pobiera cały dokument raz i wykonuje wszystkie przejścia lokalnie. Nie wysyłaj wyborów do serwera.
- Proxy `/api` musi działać zarówno w development, jak i podglądzie produkcyjnego buildu. Nie dodawaj niepotrzebnej konfiguracji CORS.

Proponowana struktura, jeśli repo jest puste:

```text
frontend/
backend/
content/legend.json
compose.yaml
.env.example
README.md
CLAUDE.md
```

Zachowuj zastane konwencje i lockfile. Nie twórz równoległego szkieletu. Nie dodawaj biblioteki, jeśli prosty kod wystarczy w tym zakresie.

## Kontrakt danych

Zamroź kontrakt na początku pracy; frontend, backend i autor treści używają jednego fixture.

```text
Story: id, title, intro, characters[], nodes[]
Character: id, name, description, entry_node_id
Decision: id, type="decision", text, choices[]
Choice: id, text, consequence, next_node_id
Ending: id, type="ending", title, text
```

ID węzłów są unikalne w historii, postaci również, a ID opcji są unikalne w scenie. Wszystkie wejścia i cele muszą istnieć. Graf jest bez cykli i bez nieosiągalnych węzłów. Każda trasa od wejścia postaci ma dokładnie 6 węzłów decyzyjnych i kończy się finałem. Zakończenia nie mają przejść. Waliduj graf małym skryptem przed importem, nie ręcznie wybierając jedną szczęśliwą ścieżkę.

Narracja jest zwykłym tekstem z akapitami; nie renderuj dowolnego HTML. Nie hardkoduj treści ani ID postaci w komponentach. Nie buduj ogólnego silnika RPG ani języka warunków.

## Stan i UI

Stan gry: postać, bieżący węzeł, liczba wykonanych decyzji, wybrana konsekwencja i jej cel. Wybór nalicza decyzję raz, a „Dalej” tylko zmienia scenę. Chroń przed podwójnym kliknięciem. Wybór postaci nie jest decyzją fabularną.

Bez localStorage i serwerowego zapisu. Odświeżenie resetuje rozgrywkę; poinformuj o tym na starcie. Nowa gra wraca do wyboru postaci. Nie wprowadzaj wersjonowania sesji, bo sesji trwałych w v0 nie ma.

Minimum UI: 360 px bez poziomego przewijania, zawijanie długich opcji, czytelne akapity, duże przyciski, semantyczne elementy i widoczny fokus. Po zmianie sceny ustaw sensownie fokus. Użyj systemowych fontów, bez ilustracji i ozdobnych animacji wymagających dodatkowej pracy. Komunikaty po polsku.

## PWA i sieć

Cache’uj powłokę aplikacji, nie API. Po pobraniu historii gra działa w pamięci i nie potrzebuje sieci do następnych decyzji. Nie obiecuj gry offline po ponownym otwarciu ani wznowienia. Bez sieci powłoka ma wyświetlić zrozumiały komunikat i możliwość ponowienia pobrania.

Testuj service worker i instalację na produkcyjnym buildzie, przez localhost lub HTTPS. Bez gotowego hostingu HTTPS sprawdź instalację lokalnie na Chrome/desktop; nie poświęcaj limitu na budowę infrastruktury. Zwykły HTTP przez IP komputera w LAN nie jest podstawą odbioru PWA na telefonie. Zanotuj rzeczywiście sprawdzone środowisko.

## Praca w zespole

- A: komponenty, stan gry, integracja API.
- B: backend, baza, Compose, importer i walidator.
- C: własne teksty i finalny `content/legend.json`.
- D: szkielet frontendu, neutralny fixture, konfiguracja PWA, osobny CSS, odbiór i README.

Nie nadpisuj pracy innych osób. Zmiana kontraktu wymaga skoordynowania wszystkich używających go modułów. Wybieraj jeden atomowy task i kończ jego kryterium akceptacji. Nie rozszerzaj zakresu „przy okazji”.

## Weryfikacja i zakończenie

Przeczytaj rzeczywiste skrypty przed uruchomieniem komend. Przy inicjalizacji udokumentuj start bazy/API, import treści, start frontendu, build i preview. Nie twierdź, że komenda istnieje lub test przeszedł, jeśli tego nie sprawdzono.

Minimalny odbiór:

1. Build frontendu i kontrola typów przechodzą.
2. Walidator akceptuje finalną historię; odrzuca przykłady z brakującym celem, cyklem i niepoprawną liczbą decyzji.
3. Ponowny import nie duplikuje rekordu; API odczytuje treść z bazy.
4. Pełne przejście ma 6 decyzji; sprawdzone oba wejścia i finały, konsekwencje, nowa gra i szybkie dwukrotne kliknięcie.
5. Zmierzono czas czytania; autor sprawdził wszystkie opcje i konsekwencje.
6. Mobilny układ, klawiatura, instalacja PWA i zachowanie bez API zostały sprawdzone i opisane.
7. README pozwala uruchomić demo i opisuje brak zapisu oraz ograniczenia offline.

Nie buduj nowego frameworka E2E ani rozbudowanego CI dla tego demo. Mały walidator i ręczny odbiór krytycznej ścieżki są obowiązkowe. Korzystaj z istniejących testów, jeśli projekt już je ma.

Po 2 godzinach musi istnieć pełna pierwsza wersja tekstów. Po 3 godzinach nie dodawaj funkcji. Ostatnia godzina jest przeznaczona na błędy blokujące i przekazanie. Przy zagrożeniu terminu skracaj opisy i ozdobniki; nie ukrywaj niespełnionych wymagań. Nie wdrażaj na płatną infrastrukturę ani nie publikuj bez polecenia zespołu.
