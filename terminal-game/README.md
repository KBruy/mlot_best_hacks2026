# Mostek Czarownic

Krótki spacer z legendą (do 10 minut) wokół kościoła św. Marii Magdaleny we
Wrocławiu. Gra przekazuje wrocławską legendę o Mostku Czarownic tam, gdzie się
wydarzyła: narracja wie, z której strony kościoła stoisz, i prowadzi cię pod wieże,
a potem na Rynek, pod pręgierz.

Działa tylko na miejscu. Bez lokalizacji albo dalej niż 250 m od kościoła legenda
pozostaje zablokowana („podejdź bliżej, żeby ją odblokować”). Ten prototyp działa
w terminalu, a GPS jest symulowany.

## Szybki start

Wszystkie polecenia uruchamiaj z katalogu `terminal-game/`:

```
cd terminal-game
uv run python main.py --trasa --mapa   # spacer po prawdziwej trasie + Street View w przeglądarce
uv run python main.py --demo           # najszybsze przejście, bez spaceru
uv run python -m unittest              # testy
```

Bez `uv` działa też `python3 main.py` (Python 3.9+, tylko biblioteka standardowa).

## Dokumentacja

- [`docs/ARCHITEKTURA.md`](docs/ARCHITEKTURA.md): jak to jest zbudowane, przepływ danych, decyzje i ich powody, następne kroki.
- [`docs/FORMAT_HISTORII.md`](docs/FORMAT_HISTORII.md): format `story.json` i przepisy (nowa scena, zakończenie, współrzędne, panoramy).
- [`docs/HANDOFF_POSTACIE.md`](docs/HANDOFF_POSTACIE.md): wszystkie postacie, z legendy i dopisane do gry.

## Jak to działa

Historia ma cztery fazy i prawdziwe rozgałęzienia. Między punktami kluczowymi
gracz idzie różnymi scenami, a w punktach kluczowych drogi się spotykają.

1. **Odblokowanie:** pozycja musi być w promieniu 250 m od kościoła. Strefa
   (zachód, południe, północ, wschód albo „ogólna”) decyduje o pierwszych słowach,
   np. „Stań twarzą do kościoła i spójrz w lewo, wzdłuż ulicy”.
2. **Faza 1, kościół:** panna z kamienicy przy Rynku wybiera drogę: próżność
   (jak w legendzie), miłość do czeladnika albo intrygę zazdrosnej kuzynki.
   Każda droga to inna scena i inne wybory.
3. **Spacer pod wieże, faza 2, wyrok (punkt kluczowy):** każda droga kończy się
   klątwą ojca i porwaniem na mostek, ale z innym powodem. Potem młoda czarownica
   słyszy od starej panny jej własną historię i postanawia pomóc.
4. **Spacer na Rynek** przez Kurzy Targ (ok. 170 m, 2 minuty), **faza 3, Rynek
   (punkt kluczowy):** starzec pod pręgierzem i trzy różne scenariusze: pomoc,
   kradzież różdżki albo targi. Każdy prowadzi do innej sceny i innych zakończeń
   (6 zakończeń, w tym takie, w którym czarownica sama trafia na mostek).
5. **Faza 4, widok z kościoła:** zakończenie, widok z mostka, odsłonięcie
   bohaterów (Tekla, Martynka, czarodziej Michał), zestawienie „Twoja wersja
   a legenda” i wynik zgodności X/6.

Każda ścieżka ma 6 decyzji, a wszystkich ścieżek jest 729 (9 różnych ciągów scen).
Imiona bohaterów pojawiają się dopiero na końcu. Szacowany czas: ok. 3,5 minuty
chodzenia i 4–5 minut czytania.

Blokada działa tylko na starcie. W trakcie spaceru gra pokazuje odległość do celu,
a gdy GPS nie łapie przystanku, możesz wpisać `j` („jestem na miejscu”).

## Uruchomienie

```
uv run python main.py            # symulacja: przy każdym odczycie GPS wybierasz, gdzie stoisz
uv run python main.py --trasa    # odtwarza prawdziwy spacer (ok. 260 m), krok 10 m co 0,5 s
uv run python main.py --trasa --mapa        # to samo + spacer na żywo na mapie Google
uv run python main.py --trasa --tempo 0     # spacer od razu, bez czekania
uv run python main.py --demo     # prezentacja: start pod wieżami, przystanki zaliczane od razu
uv run python main.py --gps 51.0980,17.0365   # własna pozycja startowa (tu: daleko, blokada)
uv run python main.py --no-gps   # brak zgody na lokalizację
uv run python main.py --tylko-trasa --mapa   # sam spacer bez historii, do sprawdzania punktów w Street View
```

`--mapa` uruchamia lokalną stronę (http://127.0.0.1:8877/, port zmienisz przez
`--port`) i otwiera ją w przeglądarce. Strona pokazuje **Google Street View** (osadzony
bez klucza API) i w rogu małą mapę satelitarną, które co chwilę pytają grę o pozycję:
- w drodze widać najbliższą sprawdzoną panoramę z ulicy, zwróconą w kierunku marszu,
- na przystankach ustalone ujęcia (pod wieżami kamera w górę, na Rynku pręgierz),
- w fazie 4 panoramę z samego mostka między wieżami (zdjęcie sferyczne autorstwa belu p. fly).

Osadzony Street View sam wybiera najbliższą panoramę, także zdjęcia użytkowników,
dlatego gra pokazuje tylko punkty z listy `streetview.anchors` w `story.json`
(oficjalne panoramy z ulicy, sprawdzone na trasie). Działa z każdym trybem GPS.

(albo `python3 main.py`). Wpisz numer opcji i Enter, po każdym wyniku Enter
przechodzi dalej. `q` albo Ctrl+C kończy grę. Kolory działają w terminalu,
a wyłączysz je zmienną `NO_COLOR=1`.

**Trasa** (`route` w `story.json`) pochodzi z Google Maps: ul. Św. Marii Magdaleny →
róg Szewskiej → pod wieże → Kurzy Targ → pręgierz, razem ok. 260 m i 3–4 minuty.
W trybie `--trasa` gra przesuwa się po niej co ok. 10 m i sama pokazuje postęp,
tak jak zrobiłaby to aplikacja z prawdziwym GPS.

**Współrzędne** w `story.json` są odczytane z Google Maps (zdjęcie satelitarne
i Street View). Wieże z mostkiem stoją od zachodu, przy ul. Szewskiej, a mostek
łączy wieżę północną z południową, więc od północy i południa widać go tylko z boku.
Przed testem w terenie warto potwierdzić strefy telefonem na miejscu.

## Testy

```
uv run python -m unittest -v
```

Testy przechodzą wszystkie 729 ścieżek dla każdej strefy (zawsze 6 decyzji, 2–3 opcje,
istniejące zakończenie, wynik 0–6) i sprawdzają m.in.:
- że wybory prowadzą do naprawdę różnych scen, a punkty kluczowe (wyrok, Rynek)
  są na każdej ścieżce we właściwej kolejności,
- że wyrok zawsze kończy się na mostku, a czarownica zawsze postanawia pomóc,
- że wcześniejsza droga zmienia wyrok i opowieść starej panny,
- wykrywanie stref, blokadę bez GPS i z daleka, odblokowanie po podejściu,
- spacer: czekanie na dotarcie, odległość do celu, pominięcie przez `j`,
- odtwarzanie trasy: długość zgodna z Google Maps, każdy odcinek kończy się na przystanku,
- podgląd na żywo: strona, pozycja, wybór panoram Street View w drodze, na przystankach
  i w finale, zdarzenia gry i flaga `--mapa`,
- że spacer i czytanie mieszczą się w 10 minutach,
- że imiona pojawiają się dopiero na końcu,
- błędne dane, `q`, Ctrl+C, restart, zawijanie tekstu, kolory i opcje wiersza poleceń.

## Pliki

- `mapa.py`: podgląd spaceru na żywo (lokalny serwer ze stroną: Street View i mapa Google).
- `main.py`: gra, mały silnik (warunki, walidacja, punktacja), lokalizacja
  (odległość, strefy, spacer) i symulowany GPS.
- `story.json`: cała treść jako graf scen (`start`, `scenes`: każda opcja ma `next`
  z następną sceną albo `null` na końcu) i dane miejsca: `location` (środek, zasięg, strefy),
  `stops` (przystanki spaceru), `route` (trasa piesza), `streetview` (panoramy),
  `test_points` (punkty do symulacji). Teksty mogą mieć
  warianty `{"if": {"pole": ["wartość"]}, "text": "..."}` zależne od strefy
  i wcześniejszych wyborów.
- `test_game.py`: testy.
