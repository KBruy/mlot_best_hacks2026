# Handoff: postacie w „Mostku Czarownic”

Stan na 2026-10-10, gałąź `terminal_game`. Ten plik opisuje wszystkie postacie z obecnej
historii: kim są, skąd pochodzą (z legendy czy dopisane do gry), w których scenach
występują i czego pilnować przy ich zmienianiu.

## Kontekst w trzech zdaniach

Gra to krótki spacer z legendą (do 10 minut) wokół kościoła św. Marii Magdaleny
i na Rynek, z symulowanym GPS. Cała treść siedzi w `story.json` jako graf scen
(`scenes`, każda opcja ma `next`), a każda ścieżka ma 6 decyzji w 4 fazach:
kościół → wyrok pod wieżami → Rynek → widok z mostka. Źródło legendy:
`docs/LEGENDY.pdf` (rozdział 2, „Mostek Czarownic”).

Uruchomienie: `uv run python main.py --trasa --mapa`, testy: `uv run python -m unittest`.

## Zasady, które dotyczą wszystkich postaci

- **Bez imion w trakcie gry.** Imiona Tekli, Martynki i Michała padają dopiero w finale,
  w sekcji „Kim byli bohaterowie?” (`reveal`) i w zestawieniu z legendą (pola `fact`).
  W scenach używamy opisów: „panna”, „stara panna”, „młoda czarownica”, „starzec”,
  „czarodziej”. Pilnuje tego test `test_names_are_revealed_only_at_the_end`.
- **Gracz jest kobietą w obu aktach** (najpierw panna, potem czarownica), więc formy
  żeńskie („pomogłabyś”, „umknęłaś”) są poprawne. Unikamy form męskich typu „przyszedłeś”.
- **Narracja w drugiej osobie, czas teraźniejszy**, zaimki małą literą („ty”, „ciebie”).
- **Stałe punkty legendy dzieją się na każdej ścieżce:** klątwa ojca i porwanie panny
  na mostek (scena `wyrok`) oraz decyzja czarownicy, że pomoże (scena `mostek`).
  Pilnują tego testy z klasy `Branching`.

## Gracz („ty”)

| | |
|---|---|
| Rola | Faza 1–2: panna z kamienicy przy Rynku. Od sceny `mostek`: młoda czarownica. |
| Źródło | Konwencja gry: gracz przeżywa legendę z perspektywy dwóch bohaterek. |
| Uwagi | Przejście między rolami jest jawne w tekście („Teraz jesteś młodą czarownicą”). |

## Postacie z legendy

### Panna z kamienicy (w legendzie: Tekla)

| | |
|---|---|
| Kim jest | Córka bogatego mieszczanina, „najpiękniejsza panna we Wrocławiu”. Później stara panna zamiatająca mostek, z twarzą czarną od kurzu. |
| Sceny | Gracz: `dom`, `bal`, `czeladnik`, `plotka`, `wyrok`. Postać niezależna (stara panna): `mostek`, wspomniana w `starzec`, `zyczenie`, `kradziez`, `uklad` i we wszystkich zakończeniach. |
| W legendzie | Piękna, próżna i leniwa, nie chce wyjść za mąż („Na cóż mi mąż? Żebym robotę jeno miała?”), przeklęta przez ojca, porwana na mostek między wieżami, by zamiatać go do końca świata. Uwolniona dzięki Martynce. |
| W grze | Ma trzy drogi (pole `sciezka`): **próżność** (zgodna z legendą), **miłość do czeladnika** albo **ofiara intrygi kuzynki** (obie dopisane). W scenie `mostek` opowiada czarownicy swoją wersję, zależną od drogi. |
| Los w zakończeniach (`los`) | `wolna`, `rok` (wolna po roku), `zamiana` i `podstep` (wolna); `moc` i `ucieczka` (zostaje na mostku). |

### Młoda czarownica (w legendzie: Martynka)

| | |
|---|---|
| Kim jest | Młoda czarownica przysłana do pomocy starej pannie. Postać gracza w drugiej połowie gry. |
| Sceny | `mostek`, `starzec`, `zyczenie`, `kradziez`, `uklad`, zakończenia. |
| W legendzie | Dobra czarownica, która wypytuje Teklę o jej winy, bierze jej miotłę, leci na Rynek, pomaga czarodziejowi Michałowi znaleźć różdżkę i w nagrodę prosi o uwolnienie Tekli. |
| W grze | Może pomóc (legenda), ukraść różdżkę albo się targować. Niezależnie od reakcji na mostku zawsze postanawia pomóc (stały punkt). W zakończeniu `zamiana` sama trafia na mostek, co tłumaczy nazwę „Mostek Czarownic”. |

### Starzec / czarodziej (w legendzie: czarodziej Michał)

| | |
|---|---|
| Kim jest | Dziwny, gderliwy starzec łażący na czworaka pod Ratuszem, przy pręgierzu. Zgubił okulary i różdżkę, a bez różdżki nie ma mocy. Okazuje się czarodziejem. |
| Sceny | `starzec` (punkt kluczowy na Rynku), `zyczenie`, `kradziez`, `uklad`, zakończenia `ucieczka` i `podstep`. |
| W legendzie | „Pomogłabyś, zamiast się gapić!” burczy na Martynkę. Wdzięczny za odnalezioną różdżkę spełnia jedno życzenie. |
| W grze | Trzy oblicza zależnie od wyboru gracza: wdzięczny (spełnia życzenie), okradziony (żąda zwrotu różdżki) albo przebiegły (proponuje układ: uwolni pannę, jeśli czarownica zajmie jej miejsce). Kwestia „Pomogłabyś, zamiast się gapić!” jest wzięta z legendy. |

### Ojciec

| | |
|---|---|
| Kim jest | Bogaty mieszczanin z kamienicy przy Rynku, ojciec panny. |
| Sceny | Wspomniany w `dom`, `bal`, `czeladnik`, `plotka`; główna rola w `wyrok` (punkt kluczowy). |
| W legendzie | Rozsierdzony lenistwem i próżnością córki przeklina ją. |
| W grze | Zawsze wypowiada klątwę („Przeklinam cię!”), ale z innego powodu w każdej drodze: za bale i śmiech z kawalerów (próżność), za wybór czeladnika wbrew jego woli (miłość) albo bo uwierzył plotce o lenistwie córki (intryga). Słowa nie da się cofnąć, nawet gdy panna błaga. |

### Matka

| | |
|---|---|
| Kim jest | Matka panny, która od rana sama szoruje garnki. |
| Sceny | `dom` (prosi o pomoc), `bal` (wstrzymuje oddech przy oświadczynach, razem z ojcem). |
| W legendzie | Załamuje ręce i prosi córkę o pomoc, ale Tekla jej nie słucha. |
| W grze | Postać tła. Jej prośba o pomoc to pierwszy wybór gry. |

### Syn bogatego kupca (kawaler)

| | |
|---|---|
| Kim jest | Kawaler, który nie spuszczał z panny oczu na balu i następnego dnia prosi o jej rękę. |
| Sceny | `bal` (tylko na drodze próżności). |
| W legendzie | Uogólnienie z legendy: Tekla „chłopcom w głowach zawracała, choć o zamążpójściu nie myślała”. |
| W grze | Panna może go wyśmiać lub zwodzić (zgodnie z legendą) albo się zgodzić, ale wtedy zrywa zaręczyny, gdy słyszy, ile pracy czeka żonę kupca. |

## Postacie dopisane do gry

Tych postaci nie ma w legendzie. Tworzą alternatywne drogi, żeby wybory naprawdę
prowadziły do innych scen. W zestawieniu na końcu gry te drogi liczą się jako
niezgodne z legendą (✗).

### Czeladnik

| | |
|---|---|
| Kim jest | Młody czeladnik z warsztatu ojca, zakochany w pannie. |
| Sceny | `dom` (wybór „Zajrzeć do warsztatu”), `czeladnik`; wraca w `wyrok` i w opowieści starej panny w `mostek`. |
| W grze | Otwiera drogę miłości (`sciezka: milosc`). Panna może odmówić kandydatowi ojca, uciec z czeladnikiem nocą albo spotykać się z nim potajemnie. |
| Uwaga | Motyw jest echem innej wrocławskiej legendy z `docs/LEGENDY.pdf` (o kamiennej głowie: czeladnik i córka mistrza), ale w grze to osobna, wymyślona postać. |

### Stary bogaty kupiec

| | |
|---|---|
| Kim jest | Kandydat na męża wybrany przez ojca. Nie mówi ani słowa. |
| Sceny | `czeladnik`. |
| W grze | Przychodzi po odpowiedź i wychodzi obrażony, jeśli panna mu odmówi. |

### Zazdrosna kuzynka

| | |
|---|---|
| Kim jest | Kuzynka, która „zawsze zazdrościła” pannie. |
| Sceny | `dom` (wybór „Zostać i pomóc matce”), `plotka`; wraca w opowieści starej panny w `mostek`. |
| W grze | Otwiera drogę intrygi (`sciezka: intryga`): rozpuszcza po Rynku plotkę, że panna jest leniwa i próżna, aż ojciec w nią uwierzy. Pokazuje legendę z drugiej strony: kara mogła spaść na kogoś, kto na nią nie zasłużył. |

### Postacie epizodyczne

| Postać | Scena | Rola |
|---|---|---|
| Przyszła teściowa | `bal`, opcja „Zgodzić się” | Wylicza, ile pracy czeka żonę kupca, przez co panna zrywa zaręczyny. |
| Straż przy bramie miasta | `czeladnik`, opcja „Uciec nocą z czeladnikiem” | Rozpoznaje córkę bogatego mieszczanina; ojciec odbiera ją rano z wartowni. |

## Gdzie co zmieniać

- **Teksty postaci:** `story.json` → `scenes.<id>` (pola `scene`, `options[].text`,
  `options[].result`). Teksty zależne od wcześniejszych wyborów to listy wariantów
  `{"if": {"sciezka": ["milosc"]}, "text": "..."}`.
- **Odsłonięcie imion:** `story.json` → `reveal`.
- **Fakty z legendy pokazywane na końcu:** `story.json` → `scenes.<id>.fact`
  (tu imiona są dozwolone, bo zestawienie pojawia się po odsłonięciu).
- **Nowa postać albo nowa droga:** dodaj scenę do `scenes`, podepnij ją przez `next`
  i dopisz nowe wartości do `state`. Walidacja (`main.validate_story`) i testy wyłapią
  martwe sceny, ścieżki o innej liczbie decyzji niż 6 i brakujące zakończenia.

## Otwarte kwestie

- Czeladnik, kuzynka i stary kupiec są wymyśleni. Jeśli gra ma być maksymalnie wierna
  legendzie, warto rozważyć, czy zostawić ich jako jawne „alternatywne wersje”.
- Polskie teksty nie były czytane przez korektora.
- Daty i szczegóły historyczne mostka (np. godziny wejścia na Mostek Pokutnic) nie są
  zweryfikowane; w grze jest tylko „godziny sprawdź przy kościele”.
