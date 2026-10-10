# Mostek Czarownic

Krótki spacer z legendą (do 10 minut) wokół kościoła św. Marii Magdaleny we
Wrocławiu. Gra przekazuje wrocławską legendę o Mostku Czarownic tam, gdzie się
wydarzyła: narracja wie, z której strony kościoła stoisz, i prowadzi cię pod wieże,
a potem na Rynek, pod pręgierz.

Działa tylko na miejscu. Bez lokalizacji albo dalej niż 250 m od kościoła legenda
pozostaje zablokowana („podejdź bliżej, żeby ją odblokować”). Ten prototyp działa
w terminalu, a GPS jest symulowany.

## Jak to działa

1. **Odblokowanie:** pozycja musi być w promieniu 250 m od kościoła. Strefa
   (zachód, południe, północ, wschód albo „ogólna”) decyduje o pierwszych słowach,
   np. „Stań twarzą do kościoła. Wieże masz po lewej”.
2. **Akt I, przy kościele:** grasz panną z kamienicy przy Rynku (3 decyzje).
3. **Spacer pod wieże** (ok. minuty), **akt II:** jesteś młodą czarownicą, a mostek
   jest nad twoją głową (1 decyzja).
4. **Spacer na Rynek** przez Kurzy Targ (ok. 170 m, 2 minuty), pod pręgierz: dziwny starzec i życzenie
   (2 decyzje).
5. **Koniec:** zakończenie, odsłonięcie bohaterów (Tekla, Martynka, czarodziej
   Michał), zestawienie „Twoja wersja a legenda” i wynik zgodności X/6.

Imiona bohaterów pojawiają się dopiero na końcu. Stałe punkty legendy dzieją się
na każdej trasie: wybór niezgodny z legendą ma w fabule skutek, który prowadzi
z powrotem do niej. Szacowany czas: ok. 3 minuty chodzenia i 4–5 minut czytania.

Blokada działa tylko na starcie. W trakcie spaceru gra pokazuje odległość do celu,
a gdy GPS nie łapie przystanku, możesz wpisać `j` („jestem na miejscu”).

## Uruchomienie

```
uv run python main.py            # symulacja: przy każdym odczycie GPS wybierasz, gdzie stoisz
uv run python main.py --trasa    # odtwarza prawdziwy spacer (ok. 260 m), krok co ok. 1 s
uv run python main.py --trasa --mapa        # to samo + spacer na żywo na mapie Google
uv run python main.py --trasa --tempo 0     # spacer od razu, bez czekania
uv run python main.py --demo     # prezentacja: start pod wieżami, przystanki zaliczane od razu
uv run python main.py --gps 51.0980,17.0365   # własna pozycja startowa (tu: daleko, blokada)
uv run python main.py --no-gps   # brak zgody na lokalizację
```

`--mapa` uruchamia lokalną stronę (http://127.0.0.1:8765/, port zmienisz przez
`--port`) i otwiera ją w przeglądarce. Strona ma osadzoną mapę Google ze zdjęciem
satelitarnym i co chwilę pyta grę o pozycję, więc pinezka przesuwa się razem ze
spacerem w terminalu. Działa z każdym trybem GPS, także z menu.

(albo `python3 main.py`). Wpisz numer opcji i Enter, po każdym wyniku Enter
przechodzi dalej. `q` albo Ctrl+C kończy grę. Kolory działają w terminalu,
a wyłączysz je zmienną `NO_COLOR=1`.

**Trasa** (`route` w `story.json`) pochodzi z Google Maps: ul. Św. Marii Magdaleny →
róg Szewskiej → pod wieże → Kurzy Targ → pręgierz, razem ok. 260 m i 3–4 minuty.
W trybie `--trasa` gra przesuwa się po niej co ok. 20 m i sama pokazuje postęp,
tak jak zrobiłaby to aplikacja z prawdziwym GPS.

**Współrzędne** w `story.json` są odczytane z Google Maps (zdjęcie satelitarne
i Street View). Wieże z mostkiem stoją od zachodu, przy ul. Szewskiej, a mostek
łączy wieżę północną z południową, więc od północy i południa widać go tylko z boku.
Przed testem w terenie warto potwierdzić strefy telefonem na miejscu.

## Testy

```
uv run python -m unittest -v
```

Testy przechodzą wszystkie trasy dla każdej strefy (zawsze 6 decyzji, 2–3 opcje,
istniejące zakończenie, wynik 0–6) i sprawdzają m.in.:
- stałe punkty legendy przy każdym wyborze i to, że każda scena reaguje na poprzedni wybór,
- wykrywanie stref, blokadę bez GPS i z daleka, odblokowanie po podejściu,
- spacer: czekanie na dotarcie, odległość do celu, pominięcie przez `j`,
- odtwarzanie trasy: długość zgodna z Google Maps, każdy odcinek kończy się na przystanku,
- mapę na żywo: strona, pozycja, nakładka na GPS i flaga `--mapa`,
- że spacer i czytanie mieszczą się w 10 minutach,
- że imiona pojawiają się dopiero na końcu,
- błędne dane, `q`, Ctrl+C, restart, zawijanie tekstu, kolory i opcje wiersza poleceń.

## Pliki

- `mapa.py`: podgląd spaceru na żywo (lokalny serwer ze stroną i mapą Google).
- `main.py`: gra, mały silnik (warunki, walidacja, punktacja), lokalizacja
  (odległość, strefy, spacer) i symulowany GPS.
- `story.json`: cała treść i dane miejsca: `location` (środek, zasięg, strefy),
  `stops` (przystanki spaceru), `test_points` (punkty do symulacji). Teksty mogą mieć
  warianty `{"if": {"pole": ["wartość"]}, "text": "..."}` zależne od strefy
  i wcześniejszych wyborów.
- `test_game.py`: testy.
