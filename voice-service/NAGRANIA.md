# Nagrania głosów: „Mostek Czarownic”

Kto co nagrywa, pod jaką nazwą pliku i jaki tekst czyta. Wymagania techniczne (10–20 s, jedno podejście, cichy pokój, zgoda na klonowanie) są w [README.md](README.md#wymagania-dotyczące-nagrania).

## Podsumowanie

| Osoba    | Pliki (wszystkie są w `voices/`)                                                                    |
| -------- | --------------------------------------------------------------------------------------------------- |
| Adrian   | `adrian_neutral.wav` ✅, `adrian_starzec.wav` ✅                                                    |
| Krystian | `krystian_neutral.wav` ✅, `krystian_kawaler.wav` ✅                                                |
| Andrzej  | `andrzej_neutral.wav` ✅, `andrzej_ojciec.wav` ✅                                                   |
| Ola      | `ola_neutral.wav` ✅, `ola_panna.wav` ✅, `ola_stara_panna.wav` ✅, `ola_wiedzma.wav` ✅, `ola_kuzynka.wav` ✅ |

Wszystkie 11 próbek jest nagranych. Profile postaci są w `characters.yaml`. Przypisanie głosów do akapitów legendy i plików audio: [NARRACJA.md](NARRACJA.md) (Mostek Czarownic) i [NARRACJA-kamienna-glowa.md](NARRACJA-kamienna-glowa.md).

## Kto gra kogo

| Postać w grze                   | Głos            | Plik używany przez serwis  |
| ------------------------------- | --------------- | -------------------------- |
| Narrator                        | Krystian        | `krystian_neutral.wav`     |
| Starzec / czarodziej            | Adrian          | `adrian_starzec.wav`       |
| Czeladnik                       | Adrian          | `adrian_neutral.wav`       |
| Ojciec                          | Andrzej         | `andrzej_ojciec.wav`       |
| Strażnik przy bramie            | Andrzej         | `andrzej_neutral.wav`      |
| Kawaler (syn kupca)             | Krystian        | `krystian_kawaler.wav`     |
| Panna (gracz, akt 1)            | Ola             | `ola_panna.wav`            |
| Stara panna                     | Ola             | `ola_stara_panna.wav`      |
| Młoda czarownica (gracz, akt 2) | Ola             | `ola_wiedzma.wav`          |
| Kuzynka                         | Ola             | `ola_kuzynka.wav`          |
| Matka, przyszła teściowa        | Ola             | `ola_neutral.wav`          |
| Stary kupiec                    | brak (nie mówi) |                            |

## Teksty

Każdy tekst czytaj w manierze postaci od początku do końca. Próbka uczy model barwy i sposobu mówienia, a nie konkretnych słów, więc tekst nie musi pokrywać się z grą. Kwestie z gry są wplecione, żeby łatwiej było wejść w postać.

### Adrian

Nic do nagrania, oba pliki już są.

### Krystian

**1. `krystian_neutral.wav`: narrator.** Spokojnie, ciepło, równym tempem, jak ktoś, kto prowadzi słuchacza przez miasto. Bez aktorzenia.

> Stoisz przy kościele świętej Marii Magdaleny. Nad tobą wznoszą się dwie wieże, a między nimi wisi wąski mostek. Mówią, że dawno temu mieszkała tu panna z kamienicy przy Rynku. Rozejrzyj się powoli, a potem ruszaj dalej, bo ta historia dopiero się zaczyna.

**2. `krystian_kawaler.wav`: kawaler, syn bogatego kupca.** Pewny siebie, trochę napuszony, z ukłonem w głosie. Wyraźnie inaczej niż narrator.

> Panno, czy zostanie pani moją żoną? Mój ojciec ma trzy statki na Odrze i najlepszy kram na całym Rynku. Nie spuszczałem z pani oczu przez cały bal. Proszę nie odpowiadać od razu, wiem, że trudno mi odmówić.

### Andrzej

**1. `andrzej_neutral.wav`: głos bazowy, używany też dla strażnika.** Naturalnie, jak w zwykłej rozmowie.

> Dawno temu, we Wrocławiu, nad brzegiem Odry stała stara kamienica. Mieszkańcy opowiadali, że po zmroku ktoś chodzi po schodach, choć drzwi są zamknięte na klucz. Jedni się śmiali, inni zapalali świece i szeptali modlitwy. Ja wiem tylko tyle, że rano zawsze pachniało dymem.

**2. `andrzej_ojciec.wav`: ojciec.** Nisko, z autorytetem, z narastającym gniewem. Ostatnie zdanie mocno, ale bez krzyku do przesteru.

> Dość balów, dość śmiechu z kawalerów! Matka od rana szoruje garnki, a ty stroisz się przed lustrem. Całe miasto o tobie mówi. Dłużej tego nie zniosę. Słyszysz mnie, córko? Przeklinam cię!

### Ola

Trzy nagrania (panna, stara panna, czarownica) to w grze dwie bohaterki, które ze sobą rozmawiają. Muszą brzmieć wyraźnie różnie. Nagraj je jedno po drugim i porównaj.

**1. `ola_neutral.wav`: głos bazowy, używany też dla matki i teściowej.** Naturalnie, jak w zwykłej rozmowie.

> Dawno temu, we Wrocławiu, nad brzegiem Odry stała stara kamienica. Mieszkańcy opowiadali, że po zmroku ktoś chodzi po schodach, choć drzwi są zamknięte na klucz. Jedni się śmiali, inni zapalali świece i szeptali modlitwy. Ja wiem tylko tyle, że rano zawsze pachniało dymem.

**2. `ola_panna.wav`: młoda panna.** Młodo, dźwięcznie, z kpiną i śmiechem. Rozpieszczona córka bogacza.

> Na cóż mi mąż? Żebym robotę jeno miała? Niech matka sama szoruje te garnki, ja idę na bal. Widziałaś, jak ten kupiecki syn się na mnie gapił? Czerwony jak burak! Może kiedyś za kogoś wyjdę. Może.

**3. `ola_stara_panna.wav`: stara panna na mostku.** Wolno, cicho, nisko, zmęczonym, lekko zachrypniętym głosem. Długie pauzy, bez energii.

> Kochałam bale i suknie… śmiałam się z kawalerów. Ojciec w końcu nie wytrzymał. Od tamtej pory zamiatam ten mostek, dzień po dniu, rok po roku. Kurz siada mi na twarzy… a ja już nawet nie pamiętam, jak wygląda Rynek z bliska.

**4. `ola_wiedzma.wav`: młoda czarownica.** Szybko, wysoko, z iskrą i uśmiechem, ciekawsko. Profil `wiedzma` już jest w `characters.yaml`.

> Leniwa panna dostała miotłę? Ha! No dobrze, dobrze, nie patrz tak na mnie. Pożycz mi ją na chwilę, polecę na Rynek i zobaczę, co da się zrobić. Trzymaj się mocno barierki, bo jak ja startuję, to wieje!

**5. `ola_kuzynka.wav`: kuzynka.** Słodko na pokaz, z jadem pod spodem, półszeptem plotkarki.

> Ach, nie mówiłam ci? Moja kuzyneczka całymi dniami leży w łóżku i patrzy w lustro. Matka haruje, a ona nawet palcem nie kiwnie. Ale ja nic nie mówiłam, dobrze? Tak tylko, między nami. Cały Rynek i tak już wie.

## Po nagraniu

1. Wrzuć pliki do `voice-service/voices/`. Nazwy dokładnie jak wyżej: małe litery, bez polskich znaków.
2. Profile postaci są już w `characters.yaml` (`narrator`, `kawaler`, `ojciec`, `straznik`, `czeladnik`, `panna`, `stara_panna`, `kuzynka`, `matka`, `tesciowa` obok `neutral`, `starzec`, `wiedzma`). Po zmianie pliku zrestartuj serwis. Postać bez własnej próbki `<głos>_<postać>.wav` używa `<głos>_neutral.wav`, np. `narrator` czyta z `krystian_neutral.wav`.
3. Sprawdź: `GET /voices` pokazuje `adrian`, `andrzej`, `krystian` i `ola`. Potem wygeneruj po jednym zdaniu dla każdej pary głos–postać i odsłuchaj.
