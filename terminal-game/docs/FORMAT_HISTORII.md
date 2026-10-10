# Format `story.json` i jak go zmieniać

Cała treść gry i dane o miejscu są w `story.json`. Ten dokument opisuje każde pole,
zasady, których pilnuje walidacja, i przepisy na typowe zmiany. Dlaczego format
wygląda tak, a nie inaczej: [`ARCHITEKTURA.md`](ARCHITEKTURA.md).

Po każdej zmianie:

```
uv run python -m unittest      # walidacja + testy wszystkich ścieżek
uv run python main.py --demo   # szybkie przejście w terminalu
```

## Teksty z warunkami

Prawie każdy tekst (akapit sceny, opcja, skutek, zakończenie) może być:

| Postać | Przykład | Znaczenie |
|---|---|---|
| napis | `"Poranek, mgła nad Odrą."` | zawsze ten sam tekst |
| jeden wariant | `{"if": {"sciezka": ["milosc"]}, "text": "..."}` | pokazany tylko, gdy warunek pasuje |
| lista wariantów | `[{"if": ...}, {"if": ...}]` | wygrywa **pierwszy** pasujący |

Warunek `if` pasuje, gdy **każde** wymienione pole stanu ma jedną z podanych wartości.
Brak `if` albo pusty `if` = pasuje zawsze. Gdy nic nie pasuje, akapit się pomija.
Nie ma wyrażeń ani `eval`, celowo.

## Pola główne

| Pole | Co zawiera |
|---|---|
| `location` | Miejsce legendy: `name`, `center` [lat, lon], `unlock_radius_m`, `default_view`, `viewpoints` (strefy: `id`, `label`, `lat`, `lon`, `radius_m`). |
| `stops` | Przystanki spaceru: `label`, `lat`, `lon`, `radius_m`, `walk` (polecenie), `arrive` (tekst po dotarciu). |
| `route` | Trasa piesza dla `--trasa`: `start` i `legs` (punkty do każdego przystanku). |
| `streetview` | Panoramy: `anchors` (sprawdzone punkty na trasie), `stops` (ujęcie na przystanku: `lat`, `lon`, `heading`, `pitch`), `finale` (+ `note`). |
| `test_points`, `demo_start` | Tylko do symulacji GPS w terminalu. |
| `state` | Pola stanu gry i ich dozwolone wartości, np. `"los": ["wolna", "moc", ...]`. |
| `intro` | `title` i `paragraphs` (z warunkami, zwykle na `widok`). |
| `start` | Id pierwszej sceny. |
| `scenes` | Graf scen (niżej). |
| `ending_by`, `endings` | Pola stanu wybierające zakończenie i same zakończenia (`title`, `paragraphs`). Klucz to wartości pól połączone `\|`, przy jednym polu po prostu `"wolna"`. |
| `finale` | Faza 4: `act` (baner) i `paragraphs` (widok z mostka). |
| `reveal` | Odsłonięcie imion: `title`, `paragraphs`. |
| `ranks` | Rangi za wynik: `min`, `title`, `text`. Musi być ranga z `min: 0`. |
| `heritage`, `look_up` | Zachęta do przekazania legendy i informacja o mostku na sam koniec. |

Pola zaczynające się od `_` (np. `_note`) to notatki dla ludzi i gra je pomija.

## Scena

```json
"wyrok": {
  "act": "FAZA 2/4: WYROK",
  "keypoint": "wyrok",
  "before": "wieze",
  "title": "Wyrok",
  "art": ["..."],
  "scene": ["akapit", {"if": ..., "text": ...}],
  "options": [
    {"text": "Wybuchnąć śmiechem", "legend": true, "set": {"reakcja": "smiech"},
     "next": "mostek", "result": ["skutek", "..."]}
  ],
  "fact": "Fakt z prawdziwej legendy do zestawienia na końcu."
}
```

| Pole | Wymagane | Znaczenie |
|---|---|---|
| `title` | tak | Nagłówek decyzji i nazwa w zestawieniu na końcu. |
| `scene` | tak | Akapity sceny (teksty z warunkami). |
| `options` | tak | 2 albo 3 opcje. |
| `fact` | tak | Jedno zdanie z prawdziwej legendy. Tu wolno używać imion. |
| `act` | nie | Baner fazy, np. `FAZA 3/4: RYNEK`. |
| `before` | nie | Id przystanku, do którego gracz musi dojść przed sceną. |
| `keypoint` | nie | Oznacza punkt kluczowy (sprawdzany w testach). |
| `art` | nie | Linie grafiki ASCII, każda krótsza niż 40 znaków. |

Opcja:

| Pole | Znaczenie |
|---|---|
| `text` | Treść opcji (może mieć warianty). |
| `legend` | `true`, jeśli wybór zgadza się z legendą (+1 do wyniku). |
| `set` | Pola stanu ustawiane po wyborze, np. `{"sciezka": "milosc"}`. Wartości muszą być w `state`. |
| `next` | Id następnej sceny albo `null`, gdy to ostatnia decyzja. |
| `result` | Akapity skutku. |

## Zasady pilnowane automatycznie

Przy starcie gry (`validate_story`) i w testach:

- każda ścieżka przez graf ma **dokładnie 6 decyzji**, a wszystkie sceny są osiągalne;
- `next` wskazuje istniejącą scenę albo `null`;
- warunki i `set` używają tylko pól i wartości z `state`;
- każda ścieżka ustawia pola z `ending_by`, a każda kombinacja ich wartości ma zakończenie;
- każda scena ma co najmniej jedną opcję zgodną i jedną niezgodną z legendą;
- punkty kluczowe są na każdej ścieżce (wyrok jako 3. decyzja, Rynek jako 5.);
- **imiona Tekli, Martynki i Michała nie pojawiają się przed `reveal`**: w scenach
  piszemy „panna”, „młoda czarownica”, „starzec”;
- spacer i czytanie mieszczą się w 10 minutach, a trasa ma 600–1000 słów.

Gracz jest kobietą w obu aktach, więc używamy form żeńskich i unikamy męskich typu
„przyszedłeś”. Narracja: druga osoba, czas teraźniejszy, zaimki małą literą.

## Przepisy

### Zmienić tekst

Edytuj odpowiedni napis w `scenes.<id>`. Jeśli tekst ma zależeć od wcześniejszego
wyboru, zamień go na listę wariantów z `if` na pole ustawiane wcześniej (np. `sciezka`).

### Dodać nową drogę w fazie 1

1. Dopisz wartość do `state.sciezka`, np. `"zemsta"`.
2. Dodaj opcję w scenie `dom` z `"set": {"sciezka": "zemsta"}` i `"next": "nowa_scena"`.
   Scena `dom` może mieć najwyżej 3 opcje, więc trzeba którąś zastąpić.
3. Dodaj `scenes.nowa_scena` z opcjami prowadzącymi do `"next": "wyrok"`; ich `set`
   ustawia `odpowiedz` (dopisz nowe wartości do `state.odpowiedz`).
4. Dopisz warianty dla nowej drogi w scenie `wyrok` (powód klątwy) i w opowieści starej
   panny w scenie `mostek`. Testy sprawdzają, że każda droga ma tu własny tekst.

### Dodać zakończenie

1. Dopisz wartość do `state.los`.
2. Ustaw ją w opcji jednej z ostatnich scen (`zyczenie`, `kradziez`, `uklad`).
3. Dodaj `endings.<wartość>` z `title` i `paragraphs`. Walidacja zgłosi brak zakończenia.

### Poprawić współrzędne po wizycie w terenie

Zmień `location.center`, `viewpoints`, `stops` i ewentualnie `route`. Testy sprawdzają
m.in., że każdy punkt widokowy wykrywa się jako swoja strefa, że trasa zaczyna się
w strefie i kończy każdy odcinek na przystanku, a jej długość to 220–300 m.

### Zaktualizować panoramy Street View

Osadzony Street View bierze najbliższą panoramę, także zdjęcia użytkowników. Dlatego
`streetview.anchors` to lista sprawdzonych punktów:

1. Dla punktów trasy (co ok. 15 m) otwórz w ramce
   `https://maps.google.com/maps?layer=c&cbll={lat},{lon}&cbp=12,0,0,0,0&output=svembed`.
2. Oficjalna panorama ma w rogu adres (np. „6 Kurzy Targ”), a zdjęcie użytkownika ma
   nazwisko autora. Do `anchors` wpisz tylko punkty z adresem.
3. Ujęcia `stops` i `finale` dobierz ręcznie (`heading` 0 = północ, ujemny `pitch` = w górę).

Testy sprawdzają, że każda panorama leży przy trasie, a ujęcia przy swoich przystankach.

### Dodać nową legendę

Skopiuj `story.json` jako wzór i zmień `location`, `stops`, `route`, `streetview`
i całą treść. Prototyp wczytuje jeden plik (`STORY_PATH` w `main.py`). Obsługa wielu
legend to zadanie dla aplikacji docelowej.
