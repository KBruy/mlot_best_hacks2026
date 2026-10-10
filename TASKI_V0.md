# Atomowe taski — 4 osoby, maksymalnie 3–4 godziny

Ten backlog zastępuje wcześniejszy plan na 24 godziny. Każdy wiersz można wkleić jako osobny task. Czas oznacza minuty aktywnej pracy właściciela. Wspólny kickoff: 10 minut dla każdej osoby, przed taskami.

## Właściciele

- **A — frontend:** komponenty, stan i przejścia, integracja API.
- **B — backend:** FastAPI, PostgreSQL, Compose, import i walidacja grafu.
- **C — narracja:** wybór legendy, ręczne teksty, docelowy JSON, korekta tempa.
- **D — uruchomienie i odbiór:** szkielet frontendu, fixture, PWA, CSS, sprawdzenie demo i README.

A edytuje logikę i komponenty, D konfigurację i osobny arkusz CSS. B utrzymuje backend i Compose, C plik finalnej historii. Po kickoffie nie blokujemy się pełnymi obszarami: frontend pracuje na fixture, backend importuje go przed dostarczeniem finalnej treści.

## Kickoff — 10 minut, cała czwórka

Wybierzcie jedną legendę i dwie postaci, zaakceptujcie graf 9 węzłów z `SCOPE_V0.md`, potwierdźcie kontrakt i dostępne środowiska. Wpiszcie ustalenia do README. D dodaje neutralny fixture; C pisze właściwą narrację. Bez dodatkowej fazy projektowania.

## A — frontend

| ID | Zadanie                                  | Min | Zależności | Kryterium akceptacji |
|---|------------------------------------------|---:|---|---|
| A01 | Dodać typy danych i stan gry             | 15 | D01, D02 | Stan obejmuje postać, węzeł, liczbę decyzji i wybraną konsekwencję; fixture się wczytuje |
| A02 | Zbudować wybór postaci                   | 15 | A01 | Dwie karty kierują do różnych pierwszych scen |
| A03 | Wyświetlić scenę i max 3 opcje           | 20 | A01 | Tekst ma akapity, przyciski pokazują opisowe, wielowierszowe opcje |
| A04 | Obsłużyć wybór i ekran konsekwencji      | 25 | A03 | Wybór nalicza jedną decyzję, pokazuje konsekwencję; „Dalej” przechodzi do celu; podwójne kliknięcie nie pomija sceny |
| A05 | Dodać finał, licznik i nową grę          | 15 | A04 | Dwa finały wyświetlają właściwy tekst; nowa gra wraca do wyboru postaci; licznik nie przekracza 6 |
| A06 | Podłączyć API i stany pobrania           | 20 | A02, B04 | Gra pobiera pełną historię; loading, błąd i ponowienie działają; po pobraniu nie odpytuje API przy wyborach |
| A07 | Sprawdzić przejścia i obsługę klawiatury | 15 | A05, A06 | Oba wejścia i finały działają; fokus jest widoczny, po przejściu trafia do nowej sceny |

**Suma: 125 minut + 10 minut kickoffu = 135 minut.**

## B — backend i baza

| ID | Zadanie | Min | Zależności | Kryterium akceptacji |
|---|---|---:|---|---|
| B01 | Utworzyć FastAPI z modelem dokumentu | 20 | kickoff | API startuje; Pydantic odrzuca niewłaściwe typy w historii |
| B02 | Dodać Compose dla API i PostgreSQL | 20 | B01 | Obie usługi startują, baza ma volume i konfigurowane połączenie |
| B03 | Dodać tabelę i skrypt importu JSON | 20 | B02, D02 | Import tworzy tabelę i wykonuje upsert; powtórzenie importu nie duplikuje historii |
| B04 | Udostępnić `GET /api/story` | 15 | B03 | Pełny dokument pochodzi z bazy; brak bazy/treści daje kontrolowane 503 |
| B05 | Dodać mały walidator wszystkich tras | 25 | B01, D02 | Sprawdza unikalne ID, cele, wejścia, osiągalność, brak cykli, dwie opcje na decyzję i 6 decyzji na każdej trasie |
| B06 | Sprawdzić poprawny i wadliwy graf | 10 | B05 | Poprawny fixture przechodzi; brak celu, cykl i 5-decyzyjna trasa są odrzucane |
| B07 | Zaimportować finalną legendę | 10 | B03, B05, C04 | Finalny plik przechodzi walidację; API pokazuje właściwe teksty |
| B08 | Opisać start i import backendu | 10 | B07 | D może uruchomić bazę/API i import na podstawie instrukcji |

**Suma: 130 minut + 10 minut kickoffu = 140 minut.**

## C — ręczna narracja

| ID | Zadanie | Min | Zależności | Kryterium akceptacji |
|---|---|---:|---|---|
| C01 | Zapisać źródło i szkic 9 węzłów | 15 | kickoff | Dwa wejścia, pięć wspólnych decyzji i dwa finały; źródło legendy odnotowane |
| C02 | Napisać dwie karty postaci i ich pierwsze sceny | 20 | C01 | Inna perspektywa dla każdej postaci, po dwie opcje z konsekwencjami |
| C03 | Napisać wspólne etapy 2–6 i dwa finały | 55 | C01 | Kompletny własny tekst, po dwie opcje z konsekwencjami; ostatni wybór rozdziela finały |
| C04 | Uzupełnić docelowy `content/legend.json` | 15 | C02, C03, D02 | Wszystkie pola i cele są zgodne z kontraktem; plik gotowy do walidacji/importu |
| C05 | Skorygować treść po pomiarze | 20 | D05 | Usunięte niespójności; jeśli poza celem 7–10 min, poprawiona długość lub jawnie zapisane odchylenie |
| C06 | Sprawdzić wszystkie warianty tekstu | 10 | C05 | Oba wejścia, 14 opcji i konsekwencji oraz oba finały są spójne; poprawiony JSON ponownie walidowany i importowany |

**Suma: 135 minut + 10 minut kickoffu = 145 minut.** C ma najbardziej napiętą pracę. Nie dodajemy kolejnych wariantów ani ozdobnych opisów przed zamknięciem pełnej historii.

## D — frontend setup, PWA i odbiór

| ID | Zadanie | Min | Zależności | Kryterium akceptacji |
|---|---|---:|---|---|
| D01 | Utworzyć Vite + React + TS | 10 | kickoff | Projekt uruchamia się, build działa; A może pracować w komponentach |
| D02 | Zapisać kontrakt i neutralny fixture | 10 | kickoff | Fixture ma 9 węzłów i 6 decyzji na trasie; neutralne treści typu „Scena 1”; A/B/C używają tych samych pól |
| D03 | Dodać minimalny CSS mobilny | 20 | D01 | 360 px bez poziomego scrolla; czytelny tekst, duże przyciski, widoczny fokus |
| D04 | Skonfigurować PWA i proxy API | 30 | D01 | Manifest, lokalne ikony i cache powłoki w buildzie; `/api` działa w dev i preview; API nie jest cache’owane |
| D05 | Zmierzyć pełne przejście właściwej legendy | 15 | A06, B07 | Zapis czasu i uwag przekazany C; sprawdzone 6 decyzji i finał |
| D06 | Sprawdzić drugi finał, mobilny UI i błędy | 20 | A07, B07, D04 | Drugie wejście/finał, reset, brak API i ponowne otwarcie bez sieci dają poprawny wynik |
| D07 | Sprawdzić instalację produkcyjnej PWA | 15 | D04, A06 | Instalacja sprawdzona na localhost/Chrome lub gotowym HTTPS; zapisane środowisko; brak fałszywej obietnicy gry offline |
| D08 | Dokończyć README i czysty start | 20 | B08, C06, D06, D07 | Instrukcja uruchamia demo; opisuje brak zapisu, zakres offline, wynik pomiaru i znane braki |

**Suma: 140 minut + 10 minut kickoffu = 150 minut.**

## Budżet i kolejność integracji

Łącznie **570 minut = 9,5 osobogodziny** zaplanowanej pracy, w tym wspólny kickoff. Dodatkowo rezerwa **30 minut na osobę** daje **11,5 osobogodziny**. Reszta okna do 4 godzin pokrywa oczekiwanie na zależności i integrację. Estymaty zakładają dostępne narzędzia i podstawową znajomość stosu; nie są gwarancją terminu.

Najważniejszy ciąg: **C01 → C03 → C04 → B07 → D05 → C05/C06 → D08**. A i B pracują na fixture, dopóki C nie dostarczy historii. Po poprawkach C06 B pomaga ponownie zaimportować treść w ramach rezerwy.

- **Po 1 h:** grywalny fragment na fixture i działające API.
- **Po 2 h:** pełna pierwsza wersja tekstów, działający UI i konfiguracja PWA.
- **Po 2,5 h:** właściwa legenda z bazy w UI; zaczyna się odbiór.
- **Po 3 h:** demo do pokazania; żadnych nowych funkcji.
- **Najpóźniej po 4 h:** przekazanie działającego demo z listą rzeczy faktycznie sprawdzonych i ewentualnych braków.

Zadanie zamykamy po sprawdzeniu jego kryterium. Nie tworzymy oddzielnej infrastruktury testów E2E, CI/CD ani panelu treści. Znalezione błędy naprawiamy w rezerwie, zaczynając od tych, które blokują ukończenie historii.
