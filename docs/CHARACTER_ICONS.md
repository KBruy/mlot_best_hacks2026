# Grafiki postaci i tła

Plik opisuje grafiki do każdej historii. Spis:

- [Mostek Czarownic](#mostek-czarownic)
- [Kamienna głowa](#kamienna-głowa)

# Mostek Czarownic

Grafiki postaci z legendy „Mostek Czarownic” (`content/legenda-czarownica.json`).
Pliki leżą płasko w `frontend/public/art/mostek-czarownic/` jako PNG z przezroczystym tłem; w historii są adresowane jako `/art/mostek-czarownic/<plik>.png`.
Przypisanie do akapitów jest w JSON: `bg` sceny i zakończenia oraz `chars: {left, right}` akapitu (lewo = gracz, prawo = rozmówca). Brak klucza = postać bez zmian, `null` = postać schodzi.
Kadr: pionowy 3:4, postać od bioder w górę.

Kolumna „Scena” podaje id sceny z JSON. Jeśli poza dotyczy konkretnej opcji, opcja jest podana po dwukropku.

## Martynka

| Plik | Scena |
|---|---|
| `martynka-neutral.png` | `mostek` |
| `martynka-wspolczucie.png` | `mostek`: skutek opcji „Zapytać, za co ją ukarano” (`czarownica: pytac`), gdy słucha historii Tekli |
| `martynka-determinacja.png` | `mostek`: „Postanawiasz jej pomóc”; `starzec` |
| `martynka-radosc.png` | zakończenie `wolna` |

## Tekla

### Młoda Tekla (faza 1–2)

| Plik | Scena |
|---|---|
| `tekla-neutral.png` | `dom` |
| `tekla-smiech.png` | `bal`: opcja „Roześmiać się: — Na cóż mi mąż?” (`odpowiedz: smiech`) |
| `tekla-kokieteria.png` | `bal`: opcja „Zwodzić go latami” (`odpowiedz: zwodzic`) |
| `tekla-zakochana.png` | `czeladnik` |
| `tekla-przerazenie.png` | `wyrok`: „— Przeklinam cię!” |
| `tekla-blaganie.png` | `wyrok`: opcja „Paść na kolana i błagać o litość” (`reakcja: blaganie`) |

### Stara Tekla (faza 2–3)

| Plik | Scena |
|---|---|
| `tekla-stara-neutral.png` | `mostek` |
| `tekla-stara-opowiesc.png` | `mostek`: skutek każdej opcji, gdy stara panna opowiada swoją historię |
| `tekla-stara-ulga.png` | zakończenie `rok` |

## Michał

| Plik | Scena |
|---|---|
| `michal-neutral.png` | `starzec` |
| `michal-moc.png` | `starzec`: skutek opcji „Podać mu różdżkę” (`rynek: pomoc`); `zyczenie`; zakończenia `wolna` i `rok` |
| `michal-gniew.png` | `kradziez` |
| `michal-chytry.png` | `uklad` |

## Ojciec

| Plik | Scena |
|---|---|
| `ojciec-neutral.png` | wzmianki w `dom`, `bal`, `czeladnik`, `plotka` |
| `ojciec-klatwa.png` | `wyrok`: „— Przeklinam cię!” |
| `ojciec-odwrocony.png` | `wyrok`: skutek opcji „Wybuchnąć śmiechem” (odwraca się bez słowa) i „Krzyknąć, że to niesprawiedliwe” (zamyka za sobą drzwi) |

## Matka

| Plik | Scena |
|---|---|
| `matka-neutral.png` | `dom`: prosi o pomoc przy garnkach |
| `matka-napiecie.png` | `bal`: wstrzymuje oddech przy oświadczynach |

## Kawaler

| Plik | Scena |
|---|---|
| `kawaler-neutral.png` | `bal`: oświadczyny |
| `kawaler-upokorzony.png` | `bal`: skutek opcji „Roześmiać się: — Na cóż mi mąż?” (`odpowiedz: smiech`) i „Zgodzić się” (`odpowiedz: zgoda`) |
| `kawaler-zawiedziony.png` | `bal`: skutek opcji „Zwodzić go latami” (`odpowiedz: zwodzic`) |

## Czeladnik

| Plik | Scena |
|---|---|
| `czeladnik-neutral.png` | `dom`: skutek opcji „Zajrzeć do warsztatu, do czeladnika” (`sciezka: milosc`) |
| `czeladnik-wyznanie.png` | `czeladnik`: wyznaje miłość |
| `czeladnik-przylapany.png` | `czeladnik`: skutek opcji „Uciec nocą z czeladnikiem” (`odpowiedz: ucieczka`) i „Spotykać się z nim potajemnie” (`odpowiedz: sekret`) |

## Postacie epizodyczne

| Plik | Scena |
|---|---|
| `kupiec-obrazony.png` | `czeladnik`: skutek opcji „Odmówić kupcowi: — Na cóż mi taki mąż?” (`odpowiedz: odmowa`) |
| `kuzynka-plotka.png` | `dom`: skutek opcji „Zostać i pomóc matce” (`sciezka: intryga`); `plotka` |
| `tesciowa-wylicza.png` | `bal`: skutek opcji „Zgodzić się” (`odpowiedz: zgoda`) |
| `straznik-przy-bramie.png` | `czeladnik`: skutek opcji „Uciec nocą z czeladnikiem” (`odpowiedz: ucieczka`) |

## Tła

Pliki leżą w `frontend/public/art/mostek-czarownic/` jako PNG 1920x1072 (16:9). Środek dołu każdego tła jest pusty, bo tam stoi postać; na telefonie tło przycina się po bokach.

| Plik | Scena |
|---|---|
| `tlo-izba.png` | `dom`, `bal`, `wyrok` |
| `tlo-warsztat.png` | `czeladnik` |
| `tlo-rynek-dzien.png` | `plotka` |
| `tlo-mostek.png` | `mostek`; zakończenia `wolna`, `rok`, `zamiana` |
| `tlo-rynek-noc.png` | `starzec`, `zyczenie`, `kradziez`, `uklad`; zakończenia `moc`, `ucieczka`, `podstep` |

# Kamienna głowa

Grafiki do legendy „Kamienna głowa” (`content/kamienna-glowa.json`).
Pliki leżą płasko w `frontend/public/art/kamienna-glowa/` jako PNG; w historii są adresowane jako `/art/kamienna-glowa/<plik>.png`.
Postacie: kadr pionowy 3:4 (896x1200), od bioder w górę, przezroczyste tło.
Przypisanie do akapitów robi się w JSON tak samo jak w Mostku Czarownic: `bg` sceny i zakończenia oraz `chars: {left, right}` akapitu (lewo = gracz, prawo = rozmówca).

Kolumna „Scena” podaje id sceny z JSON. Jeśli grafika dotyczy konkretnej opcji, opcja jest podana po dwukropku.

## Czeladnik (gracz, faza 1–2)

| Plik | Scena |
|---|---|
| `czeladnik-neutral.png` | `warsztat`; `mistrz`; `kolega` |
| `czeladnik-zakochany.png` | `warsztat`: skutek opcji „Potajemnie wykuć dla niej srebrny pierścień” (`sciezka: pierscien`); `ogrod` |
| `czeladnik-przysiega.png` | `przysiega` |

## Zbójnik (gracz po latach, faza 3–4)

| Plik | Scena |
|---|---|
| `zbojnik-neutral.png` | `szlak`; `powrot`; zakończenia `odejscie`, `ucieczka` |
| `zbojnik-gniew.png` | `odmowa`; `ofiara` i `rozmowa`: skutek opcji prowadzącej do `los: glowa` |
| `zbojnik-skrucha.png` | `ofiara`; `odmowa`: skutek opcji „Oddać całe zrabowane złoto…” (`los: ofiara`); zakończenia `ofiara`, `sad`, `pokuta` |

## Córka mistrza

| Plik | Scena |
|---|---|
| `corka-neutral.png` | `warsztat`: skutek opcji z pierścieniem; `ogrod` |
| `corka-starsza-odraza.png` | `odmowa`; `rozmowa` |

## Mistrz złotnik

| Plik | Scena |
|---|---|
| `mistrz-neutral.png` | `warsztat` |
| `mistrz-gniew.png` | `mistrz`; skutki opcji w `ogrod` i `kolega` (wyrzuca czeladnika) |
| `mistrz-chciwy.png` | `odmowa`: mistrz zaślepiony złotem |

## Pozostali

| Plik | Scena |
|---|---|
| `rywal-neutral.png` | `warsztat`; `kolega`; `ogrod` (zdradza sekret) |
| `opiekunka-neutral.png` | `ogrod` |
| `ksiadz-odmowa.png` | `ofiara`; `powrot`: skutek opcji „Najpierw wejść do katedry…” (`powrot: ofiara`) |

## Tła

PNG 1920x1072 (16:9), środek dołu pusty pod postać; na telefonie tło przycina się po bokach. `tlo-kamienna-glowa.png` to obraz zakończenia, bez miejsca na postać.

| Plik | Scena |
|---|---|
| `tlo-warsztat-zlotnika.png` | `warsztat`, `kolega` |
| `tlo-ogrod-noc.png` | `ogrod`, `rozmowa` |
| `tlo-izba-mistrza.png` | `mistrz`, `odmowa`; zakończenie `ofiara` |
| `tlo-most.png` | `przysiega` |
| `tlo-szlak-zima.png` | `szlak`; zakończenia `odejscie`, `ucieczka` |
| `tlo-ostrow-tumski.png` | `powrot`, `ofiara`; zakończenia `sad`, `pokuta` |
| `tlo-kamienna-glowa.png` | zakończenie `glowa` |
