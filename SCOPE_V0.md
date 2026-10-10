# Scope v0 — demo w 3–4 godziny

## Cel

Cztery osoby w maksymalnie 3–4 godziny wspólnej pracy dostarczają grywalną PWA z jedną legendą wrocławską. To 12–16 osobogodzin dostępności zespołu, nie 24 godziny developmentu. Ten dokument zastępuje wcześniejszy plan na 24 godziny.

Priorytet: wybrać postać → przeczytać historię → wykonać 6 wyborów → zobaczyć zakończenie. Wszystkie teksty i ścieżki przygotowuje zespół ręcznie, bez AI. Pozostałe dwie legendy należą do kolejnej wersji.

## Minimalny zakres

| Element | Decyzja na v0 | Odbiór |
|---|---|---|
| Legenda | Jedna, wybrana w pierwszych 10 minutach | Własna adaptacja, źródło zapisane w README |
| Postaci | Dwie, każda ma inną pierwszą scenę | Wybór postaci zmienia wejście do grafu |
| Przebieg | Po pierwszej decyzji ścieżki łączą się; etapy 2–6 są wspólne | Każde przejście ma dokładnie 6 decyzji |
| Wybory | Po 2 opisowe opcje na scenę | Opcje zawijają się na wiele wierszy; każda pokazuje inny tekst konsekwencji |
| Konsekwencje | Tekst wyświetlany po wyborze, przed następną sceną | Gracz widzi rezultat swojej decyzji; „Dalej” nie liczy się jako decyzja |
| Finał | Dwa zakończenia wybierane ostatnią decyzją | Oba są osiągalne; można zagrać ponownie |
| Czas historii | Cel: około 8 minut | Jedno mierzone przejście; cel 7–10 minut, odchylenie zapisane jako ograniczenie demo |
| UI | Start z wyborem postaci, scena, konsekwencja, finał | Działa na telefonie przy 360 px i na desktopie |
| PWA | Manifest, lokalne ikony, service worker przechowujący powłokę | Instalacja w obsługiwanej przeglądarce na produkcyjnym buildzie |
| Backend | FastAPI, jeden endpoint historii | Frontend pobiera pełny dokument i wykonuje grę lokalnie |
| Baza | PostgreSQL w Dockerze, jedna tabela z JSONB | Ręcznie przygotowana historia jest importowana i odczytywana przez API |

**Kompromis narracyjny:** v0 ma krótkie rozgałęzienie zależne od postaci i odmienne konsekwencje wyborów, ale nie ma dwóch całkowicie osobnych kampanii. Wcześniejsze wybory nie naliczają punktów ani nie zmieniają finału; finał zależy od ostatniego wyboru. Tak ograniczamy ilość treści i kodu.

Graf zawiera tylko **9 węzłów**: 2 alternatywne sceny pierwszej decyzji, 5 wspólnych scen decyzji 2–6 i 2 zakończenia. Teksty konsekwencji są polami opcji, nie dodatkowymi węzłami. Łącznie trzeba napisać 7 scen decyzyjnych, 14 opcji z krótkimi konsekwencjami i 2 finały.

Na czytaną ścieżkę zaplanuj orientacyjnie 900–1100 słów, łącznie z opcjami i konsekwencjami; potem zmierz rzeczywisty czas. Nie wydłużaj historii sztucznym oczekiwaniem. Jeśli tekstów nie ma na starcie, ich napisanie jest największym ryzykiem terminu.

## Architektura bez nadmiarowych elementów

- Frontend: Vite + React + TypeScript, zwykły CSS, stan w React. Bez routera i biblioteki zarządzania stanem.
- Backend: FastAPI + walidacja struktury przez Pydantic, jeden endpoint `GET /api/story` zwracający pełną historię; 503, jeśli historia/baza jest niedostępna.
- PostgreSQL: tabela `stories(id TEXT PRIMARY KEY, payload JSONB NOT NULL)`. Jeden skrypt tworzący tabelę i importujący treść przez upsert. Bez frameworka migracji i ORM, jeśli zespół nie ma gotowego szablonu.
- Ręcznie edytowany plik `content/legend.json` jest źródłem treści. Importujemy go do bazy; backend nie generuje narracji.
- Compose uruchamia bazę i API. Frontend uruchamiany lokalnie; kontener frontendu nie jest wymaganiem v0.
- Frontend używa `/api`; proxy Vite obejmuje development oraz podgląd produkcyjnego buildu.
- Brak zapisu sesji: odświeżenie rozpoczyna grę od nowa. UI informuje o tym na starcie.

Kontrakt zamrażamy w pierwszych 15 minutach:

```text
Story: id, title, intro, characters[], nodes[]
Character: id, name, description, entry_node_id
Decision: id, type="decision", text, choices[]
Choice: id, text, consequence, next_node_id
Ending: id, type="ending", title, text
```

Każda decyzja ma dwie opcje. W etapach 1–5 obie mogą prowadzić do tego samego następnego węzła, ale wyświetlają różne konsekwencje. W etapie 6 prowadzą do dwóch różnych zakończeń. Przy wyborze UI pokazuje konsekwencję; dopiero „Dalej” otwiera cel. Wybór postaci nie zwiększa licznika 6 decyzji.

## Co oznacza PWA w tym demo

Manifest, ikony i service worker umożliwiają podstawowe zachowanie aplikacji instalowalnej. W v0 **nie gwarantujemy rozpoczęcia ani wznowienia historii offline**. Po pobraniu dokumentu rozpoczęta gra może działać bez sieci do odświeżenia, bo trzyma dane w pamięci. Przy ponownym otwarciu bez połączenia powłoka wyświetla komunikat o konieczności połączenia.

Nie cache’ujemy API ani postępu. PWA sprawdzamy na produkcyjnym buildzie przez localhost lub HTTPS. Do instalacji na telefonie potrzebny jest wcześniej dostępny adres HTTPS; zwykły HTTP pod adresem komputera w LAN nie wystarcza. Bez gotowego hostingu odbiór instalacji robimy lokalnie w Chrome na desktopie. Publiczne wdrożenie nie jest wymagane.

## Poza v0

Pełne offline, zapis/wznowienie, konta, kolejne legendy, osobna kampania każdej postaci, złożone warunki i punktacja, walka/DND, ekwipunek, losowość, panel autora, ilustracje na zamówienie, audio, mapa/GPS, multiplayer, analityka, CI/CD i rozbudowana infrastruktura. Zero AI w aplikacji oraz tworzeniu treści.

## Plan czasowy

| Czas od startu | Wynik |
|---|---|
| 0:00–0:15 | Wybrana legenda i postaci, kontrakt, podział plików, neutralny fixture |
| 0:15–1:00 | Frontend przechodzi fixture; baza i API działają; autor pisze teksty |
| 1:00–2:00 | UI i PWA gotowe; pierwsza wersja całej narracji trafia do JSON |
| 2:00–2:30 | Właściwa legenda przez API, sprawdzony graf, dwa finały |
| 2:30–3:00 | Mierzone przejście, poprawki tekstów i mobilnego UI, build produkcyjny |
| 3:00–4:00 | Tylko naprawy blokujące, odbiór PWA i instrukcja demo |

Jeśli po 2 godzinach brakuje treści, autor skraca opisy konsekwencji i korzysta ze wspólnych scen. Nie dokładamy nowych gałęzi. Jeśli nie da się utrzymać jednocześnie 8 minut narracji i terminu, oddajemy krótsze, kompletne demo i jawnie zapisujemy odchylenie — nie deklarujemy spełnienia tego wymagania.

## Definicja ukończenia

1. Instrukcja uruchamia bazę, API i frontend; właściwa legenda pochodzi z PostgreSQL.
2. Obie postaci mają inne wejście; każda trasa zawiera 6 decyzji i kończy się jednym z dwóch finałów.
3. Wszystkie opcje mają tekst konsekwencji; nie ma brakujących celów, cykli ani nieosiągalnych węzłów.
4. Gra działa przy 360 px, opcje są czytelne i obsługiwane klawiaturą; szybkie dwukrotne kliknięcie nie pomija sceny.
5. Build produkcyjny działa, PWA została sprawdzona w wskazanej przeglądarce; brak sieci pokazuje zrozumiały stan.
6. Przeprowadzono pełną grę z pomiarem czasu oraz sprawdzono drugie wejście i oba zakończenia. Czas poza 7–10 minut to jawnie nieukończone wymaganie treści, nie blokada przekazania demo.
7. README opisuje start, import treści, brak zapisu i ograniczenia offline. Brak AI i sekretów w repozytorium.
