# Narracja „Mostku Czarownic”: przypisanie głosów

Propozycja: kto czyta który akapit legendy. Każdy plik poniżej odpowiada jednemu `audio_url` w `content/legenda-czarownica.json` (jeden akapit albo jeden wariant `if`). Teksty opcji nie są czytane. Próbki głosów: [NAGRANIA.md](NAGRANIA.md), profile postaci: `characters.yaml`.

## Zasady

- Całą narrację (druga osoba, „ty”) czyta **narrator**: `[Krystian, narrator]`.
- Kwestie w dialogach czytają postacie:

  | Postać | Skrypt |
  | --- | --- |
  | ojciec | `[Andrzej, ojciec]` |
  | kawaler | `[Krystian, kawaler]` |
  | starzec / czarodziej | `[Adrian, starzec]` |
  | panna (gracz w akcie 1) | `[Ola, panna]` |
  | stara panna | `[Ola, stara_panna]` |
  | młoda czarownica (gracz w akcie 2) | `[Ola, wiedzma]` |

  Wtrącenia typu „szepcze stara panna” czyta narrator.
- Fragmenty skryptu składają się dokładnie na słowa tekstu z legendy (bez myślników dialogowych), więc napisy i nagranie się zgadzają.
- Identyczne akapity mają wspólny plik: porwanie na mostek po każdej reakcji w scenie `wyrok` (`wyrok-o1-2.mp3`) i opowieść starej panny po każdej opcji w scenie `mostek` (`mostek-o1-2-*.mp3`, `mostek-o1-3.mp3`).
- Razem **71 plików**, w tym 20 z dialogiem (kilka głosów w jednym pliku).

## Generowanie

Skrypt `narrate.py` generuje wszystko na podstawie bloków z tego pliku i tekstów z legendy. Nie potrzebuje uruchomionego serwisu, klucza API ani ffmpeg. Uruchamiaj z katalogu `voice-service/`:

```bash
uv run python narrate.py --check          # spójność skryptów z legendą (szybko, bez modeli)
uv run python narrate.py dom-1            # próba na jednym pliku: odsłuchaj przed całością
uv run python narrate.py                  # wszystkie brakujące pliki
uv run python narrate.py --force bal-1    # ponowne generowanie wybranego pliku (np. po złym podejściu)
uv run python narrate.py --align-only     # tylko znaczniki czasu do istniejących WAV
uv run python narrate.py --retrim         # przytnij ogony w istniejących WAV (bez generowania)
```

**Przycinanie śmieci.** Chatterbox po zdaniu potrafi dogenerować kilka sekund szumu, buczenia albo bełkotu, czasem głośnego jak mowa. Dlatego po syntezie skrypt dopasowuje tekst do nagrania (MMS_FA) i:

- tnie każdy odcinek między pauzami 0,15 s za jego ostatnim słowem, a odcinki bez słów usuwa;
- skraca do ok. 0,3 s ciszę dłuższą niż 0,6 s między słowami wewnątrz odcinka (serwis generuje zdania krótsze niż 25 znaków razem z następnym, więc śmieci po nich nie są oddzielone pauzą);
- pauzy między zdaniami i kwestiami zostawia bez zmian.

Nowe pliki są przycinane automatycznie. Pliki wygenerowane wcześniejszą wersją skryptu popraw przez `--retrim`.

Wyniki:

| Plik | Gdzie | Commit |
| --- | --- | --- |
| WAV master (PCM 16-bit, 24 kHz, mono) | `voice-service/outputs/mostek-czarownic/<plik>.wav` | nie (`*.wav` w `.gitignore`) |
| MP3 dla frontu (CBR 64 kb/s, mono) | `frontend/public/audio/mostek-czarownic/<plik>.mp3` | tak |
| Znaczniki czasu słów | `frontend/public/audio/mostek-czarownic/<plik>.json` | tak |

- Gotowe pliki są pomijane, więc przerwane generowanie wznawia się od miejsca przerwania. Kwestie trafiają też do cache serwisu (`cache/`), więc `--force` na pliku bez zmian w skrypcie zwróci to samo nagranie; żeby dostać inne podejście, wyczyść odpowiednie pliki z `cache/` albo zmień tekst kwestii.
- Pierwsze uruchomienie pobiera modele: TTS (Chatterbox) i dopasowania (MMS_FA, ok. 1,2 GB do `~/.cache/torch`).
- Czas: TTS na CPU to ok. 10× czasu nagrania, więc całość (kilka minut audio) to rząd godziny lub dłużej. Dopasowanie to ok. 6 s na 16 s nagrania.
- Bardzo krótkie kwestie (np. „Śmiej się” i „Posłuchaj.” w `mostek-o3-1`) warto odsłuchać, bo model bywa na nich niestabilny.
- Po zmianie tekstu w legendzie popraw blok w tym pliku. `--check` (i każde uruchomienie) przerwie pracę, gdy słowa skryptu nie zgadzają się z tekstem akapitu.

## Karaoke: napisy w tempie nagrania

Cel: słowa legendy pojawiają się dokładnie wtedy, gdy lektor je wypowiada (efekt audioprzewodnika w muzeum). Front ma już komponent `NarrativeKaraoke`, dziś ze stałym tempem 60 ms na słowo.

**Format znaczników.** Plik leży obok nagrania pod tą samą nazwą z `.json`, np. `/audio/mostek-czarownic/dom-1.json`. To konwencja plików statycznych, poza kontraktem API:

```json
{"words": [{"text": "Wyobraź", "start": 0.00, "end": 0.48}, {"text": "sobie,", "start": 0.48, "end": 0.83}]}
```

`words` to słowa tekstu akapitu w kolejności (podział po spacjach, jak w `NarrativeKaraoke`), czasy w sekundach od początku MP3. Front odsłania słowo, gdy `audio.currentTime >= start`, a akapit kończy na zdarzeniu `ended`.

**Skąd czasy:**

- **Dokładnie co do słowa (zrobione w `narrate.py`):** forced alignment modelem `MMS_FA` wbudowanym w torchaudio (wav2vec2, wielojęzyczny). Znamy tekst akapitu, więc model nie rozpoznaje mowy, tylko dopasowuje znane słowa do nagrania. Bez nowych zależności. Sprawdzone na próbce `krystian_neutral.wav` (16,5 s): słowa trafiają w mowę, przerwy między zdaniami są widoczne w czasach, ostatnie słowo kończy się 0,4 s przed końcem nagrania. Myślniki dialogowe dostają czas następnego słowa.
- **Fallback we froncie, gdy `.json` nie ma (404):** po `loadedmetadata` rozłóż `audio.duration` na słowa proporcjonalnie do liczby liter, z dodatkową wagą za `.`, `?`, `!`, `,` (pauzy 0,25 s między zdaniami i 0,5 s między kwestiami).

Front: dla akapitu z `audio_url` pobiera `.json` obok MP3 (podmiana rozszerzenia), odtwarza nagranie i odsłania słowa według `start`; bez `.json` używa fallbacku, a bez `audio_url` zostaje przy obecnym stałym tempie.

## Skrypty

### `intro-1-zachod.mp3`

```text
[Krystian, narrator] Stań twarzą do kościoła. Dwie ceglane wieże masz na wprost, a wysoko między nimi wisi wąski mostek.
```

### `intro-1-poludnie.mp3`

```text
[Krystian, narrator] Stań twarzą do kościoła i spójrz w lewo, wzdłuż ulicy: tam wznosi się wieża. Wysoko na niej widać skraj wąskiego mostka, który łączy ją z drugą wieżą.
```

### `intro-1-polnoc.mp3`

```text
[Krystian, narrator] Stań twarzą do kościoła. Wieże masz po prawej. Wysoko między nimi wisi wąski mostek, choć stąd widać go tylko z boku.
```

### `intro-1-wschod.mp3`

```text
[Krystian, narrator] Stań twarzą do kościoła. Przed tobą długie, ceglane prezbiterium, a nad dachem, w oddali, wystają dwie wieże. Wysoko między nimi wisi wąski mostek.
```

### `intro-1-ogolny.mp3`

```text
[Krystian, narrator] Rozejrzyj się za dwiema ceglanymi wieżami kościoła. Wysoko między nimi wisi wąski mostek.
```

### `intro-2.mp3`

```text
[Krystian, narrator] Wrocławianie od wieków opowiadają, kto go zamiata i dlaczego. 
```

### `dom-1.mp3`

```text
[Krystian, narrator] Wyobraź sobie, że jesteś córką bogatego mieszczanina z kamienicy przy Rynku, kilka minut stąd. Wszyscy mówią, że jesteś najpiękniejszą panną we Wrocławiu.
```

### `dom-2.mp3`

```text
[Krystian, narrator] Dziś wieczorem jest bal. Matka od rana sama szoruje garnki i prosi cię o pomoc, a w warsztacie ojca młody czeladnik zerka na ciebie znad roboty.
```

### `dom-o1-1.mp3`

```text
[Krystian, narrator] Zostawiasz matkę z garnkami i biegniesz na bal. Tańczysz do świtu, a kawalerowie nie odstępują cię na krok.
```

### `dom-o2-1.mp3`

```text
[Krystian, narrator] Czeladnik czerwienieje, gdy stajesz w drzwiach. Rozmawiacie do zmroku i o balu zapominasz zupełnie.
```

### `dom-o3-1.mp3`

```text
[Krystian, narrator] Pomagasz matce do wieczora. Nie wiesz, że kuzynka, która zawsze ci zazdrościła, właśnie wychodzi na Rynek z nowiną.
```

### `bal-1.mp3`

```text
[Krystian, narrator] Następnego dnia w waszych drzwiach staje syn bogatego kupca, ten, który nie spuszczał z ciebie oczu na balu.
[Krystian, kawaler] Panno, czy zostanie pani moją żoną?
[Krystian, narrator] Rodzice wstrzymują oddech.
```

### `bal-o1-1.mp3`

```text
[Ola, panna] Na cóż mi mąż? Żebym robotę jeno miała?
[Krystian, narrator] śmiejesz się. Kawaler wychodzi czerwony jak burak, a ojciec zaciska pięści.
```

### `bal-o2-1.mp3`

```text
[Krystian, narrator] Obiecujesz „może kiedyś” i latami zawracasz mu w głowie, aż kawaler żeni się z inną. Ojciec patrzy na ciebie coraz chmurniej.
```

### `bal-o3-1.mp3`

```text
[Krystian, narrator] Mówisz „tak”, ale gdy przyszła teściowa wylicza, ile pracy czeka żonę kupca, zrywasz zaręczyny. Całe miasto plotkuje, a ojciec ma dość.
```

### `czeladnik-1.mp3`

```text
[Krystian, narrator] Czeladnik wyznaje ci miłość. Ale ojciec już wybrał ci męża: starego, bogatego kupca, który przyjdzie jutro po odpowiedź.
```

### `czeladnik-o1-1.mp3`

```text
[Krystian, narrator] Kupiec wychodzi obrażony, a ojciec blednie ze wstydu. Wie już, dla kogo odprawiasz kandydatów.
```

### `czeladnik-o2-1.mp3`

```text
[Krystian, narrator] Uciekacie, ale straż przy bramie miasta poznaje córkę bogatego mieszczanina. Rano ojciec odbiera cię z wartowni.
```

### `czeladnik-o3-1.mp3`

```text
[Krystian, narrator] Przez kilka miesięcy wymykasz się do warsztatu nocami. Aż pewnego wieczoru ojciec wraca wcześniej i zastaje was razem.
```

### `plotka-1.mp3`

```text
[Krystian, narrator] Kuzynka rozpuszcza po Rynku plotkę: że jesteś leniwa i próżna, że wyśmiewasz każdego kawalera i całe dnie przesiadujesz przed lustrem. Ludzie zaczynają szeptać, gdy przechodzisz.
```

### `plotka-o1-1.mp3`

```text
[Krystian, narrator] Całą noc jesteś królową balu. Kuzynka zgrzyta zębami, a plotka tylko rośnie: przecież widać, że myślisz wyłącznie o strojach.
```

### `plotka-o2-1.mp3`

```text
[Krystian, narrator] Harujesz od świtu do nocy, ale plotka już żyje własnym życiem. Ojciec słyszy ją w cechu, w kościele i na targu.
```

### `plotka-o3-1.mp3`

```text
[Krystian, narrator] Udajesz, że nie słyszysz. Kuzynka dokłada kolejne historie, aż w końcu trafiają do uszu ojca.
```

### `wyrok-1.mp3`

```text
[Krystian, narrator] Zadrzyj głowę. Ten wąski mostek między wieżami to miejsce, w którym skończy się twoja droga, jakkolwiek się zaczęła.
```

### `wyrok-2-proznosc.mp3`

```text
[Krystian, narrator] Ojciec staje w drzwiach, czerwony z gniewu.
[Andrzej, ojciec] Dość balów, dość śmiechu z kawalerów! Co z ciebie wyrośnie?
```

### `wyrok-2-milosc.mp3`

```text
[Krystian, narrator] Ojciec staje w drzwiach, czerwony z gniewu.
[Andrzej, ojciec] Wolisz czeladnika od woli ojca? Okryłaś nas wstydem!
```

### `wyrok-2-intryga.mp3`

```text
[Krystian, narrator] Ojciec staje w drzwiach, czerwony z gniewu.
[Andrzej, ojciec] Całe miasto mówi o twoim lenistwie i próżności! Dłużej tego nie zniosę!
```

### `wyrok-3.mp3`

```text
[Andrzej, ojciec] Przeklinam cię!
[Krystian, narrator] grzmi.
```

### `wyrok-o1-1.mp3`

```text
[Krystian, narrator] Śmiejesz się, bo przecież to tylko słowa. Ojciec odwraca się bez słowa.
```

### `wyrok-o1-2.mp3`

```text
[Krystian, narrator] Tej samej nocy coś porywa cię z łóżka. Budzisz się wysoko pod chmurami, na tym mostku nad twoją głową. W rękach trzymasz miotłę. Nie pomagają łzy, prośby ani krzyki: tak wysoko nikt cię nie słyszy.
```

### `wyrok-o2-1.mp3`

```text
[Krystian, narrator] Błagasz, ale słowo się rzekło i nawet ojciec nie może go już cofnąć.
```

### `wyrok-o3-1.mp3`

```text
[Ola, panna] To niesprawiedliwe!
[Krystian, narrator] krzyczysz, ale ojciec już zamyka za sobą drzwi.
```

### `mostek-1.mp3`

```text
[Krystian, narrator] Mijają lata. Panna zamiata mostek każdego dnia. Postarzała się, a twarz ma czarną od kurzu.
```

### `mostek-2.mp3`

```text
[Krystian, narrator] Teraz jesteś młodą czarownicą. Przysłano cię, żebyś pomagała starej pannie, bo sama już nie daje rady.
```

### `mostek-o1-1.mp3`

```text
[Krystian, narrator] Pytasz łagodnie. Stara panna długo milczy, a potem opowiada.
```

### `mostek-o1-2-proznosc.mp3`

```text
[Ola, stara_panna] Kochałam bale i suknie, śmiałam się z kawalerów
[Krystian, narrator] szepcze stara panna.
[Ola, stara_panna] Ojciec w końcu nie wytrzymał.
```

### `mostek-o1-2-milosc.mp3`

```text
[Ola, stara_panna] Kochałam czeladnika z warsztatu ojca
[Krystian, narrator] szepcze stara panna.
[Ola, stara_panna] Ojciec wolał mnie przekląć, niż na to pozwolić.
```

### `mostek-o1-2-intryga.mp3`

```text
[Ola, stara_panna] Kuzynka rozpuściła plotkę, że jestem leniwa i próżna
[Krystian, narrator] szepcze stara panna.
[Ola, stara_panna] Ojciec uwierzył jej, nie mnie.
```

### `mostek-o1-3.mp3`

```text
[Krystian, narrator] Słuchasz i coś ściska cię w gardle. Postanawiasz jej pomóc.
```

### `mostek-o2-1.mp3`

```text
[Krystian, narrator] Zamiatacie w milczeniu kilka dni, aż stara panna sama zaczyna mówić, jakby nie mogła dłużej tego dźwigać.
```

### `mostek-o3-1.mp3`

```text
[Ola, wiedzma] Leniwa panna dostała miotłę?
[Krystian, narrator] parskasz.
[Ola, stara_panna] Śmiej się
[Krystian, narrator] odpowiada.
[Ola, stara_panna] Posłuchaj.
```

### `starzec-1.mp3`

```text
[Krystian, narrator] Nocą bierzesz po cichu miotłę starej panny i lecisz na Rynek szukać pomocy. Tu, gdzie teraz stoisz.
```

### `starzec-2.mp3`

```text
[Krystian, narrator] Rynek jest pusty, tylko pod Ratuszem, przy tym pręgierzu, dziwny starzec łazi na czworaka.
[Adrian, starzec] Okulary zgubiłem i różdżkę! Bez różdżki nie mam mocy
[Krystian, narrator] burczy.
[Adrian, starzec] Pomogłabyś, zamiast się gapić!
```

### `starzec-3.mp3`

```text
[Krystian, narrator] Z miotły od razu widzisz różdżkę: leży w cieniu pręgierza, tuż obok niego.
```

### `starzec-o1-1.mp3`

```text
[Krystian, narrator] Podajesz mu różdżkę. Starzec prostuje plecy i nagle wcale nie wygląda na bezradnego.
```

### `starzec-o2-1.mp3`

```text
[Krystian, narrator] Chwytasz różdżkę, zanim starzec ją zobaczy. Drewno drży ci w dłoni, jakby było żywe.
```

### `starzec-o3-1.mp3`

```text
[Krystian, narrator] Stawiasz stopę na różdżce, zanim starzec ją zobaczy.
[Ola, wiedzma] Wiem, gdzie jest twoja różdżka. Powiem, jeśli coś dla mnie zrobisz.
[Krystian, narrator] Starzec mruży oczy.
```

### `zyczenie-1.mp3`

```text
[Adrian, starzec] Jestem czarodziejem
[Krystian, narrator] mówi starzec.
[Adrian, starzec] Dobre z ciebie dziecko. W nagrodę spełnię jedno twoje życzenie.
```

### `zyczenie-o1-1.mp3`

```text
[Krystian, narrator] Czarodziej macha różdżką. Gdzieś za dachami, między wieżami kościoła, coś błyska.
```

### `zyczenie-o2-1.mp3`

```text
[Krystian, narrator] Czarodziej macha różdżką. Czujesz moc aż w czubkach palców, a z wieży wciąż dobiega szuranie miotły.
```

### `zyczenie-o3-1.mp3`

```text
[Adrian, starzec] Sprawiedliwie
[Krystian, narrator] mruczy czarodziej i macha różdżką.
[Adrian, starzec] Za rok będzie wolna.
```

### `kradziez-1.mp3`

```text
[Adrian, starzec] Oddaj! To moja różdżka!
[Krystian, narrator] krzyczy starzec. Teraz już wiesz, kim jest: to czarodziej, a ty trzymasz całą jego moc.
```

### `kradziez-o1-1.mp3`

```text
[Krystian, narrator] Oddajesz różdżkę. Czarodziej kręci głową, ale macha nią w stronę wież:
[Adrian, starzec] Niech ci będzie. Za uczciwość, choć spóźnioną.
```

### `kradziez-o2-1.mp3`

```text
[Krystian, narrator] Machasz różdżką, a ta wyrywa ci się z ręki. Wiatr porywa cię w górę, ku wieżom. Czarodziej woła coś za tobą, ale już go nie słyszysz.
```

### `kradziez-o3-1.mp3`

```text
[Krystian, narrator] Wskakujesz na miotłę i znikasz nad dachami. Czarodziej zostaje bez mocy, a panna na mostku bez nadziei.
```

### `uklad-1.mp3`

```text
[Adrian, starzec] Jestem czarodziejem
[Krystian, narrator] syczy starzec.
[Adrian, starzec] I wiem, po co przyleciałaś: po pannę z mostka. Mogę ją uwolnić, ale ktoś musi zamiatać ten mostek. Zajmiesz jej miejsce?
```

### `uklad-o1-1.mp3`

```text
[Krystian, narrator] Kiwasz głową. Czarodziej podnosi różdżkę spod twojej stopy i macha nią raz, a potem drugi.
```

### `uklad-o2-1.mp3`

```text
[Krystian, narrator] Zdejmujesz stopę z różdżki i mu ją podajesz. Czarodziej długo na ciebie patrzy.
[Adrian, starzec] Dobre z ciebie dziecko
[Krystian, narrator] mówi w końcu i macha nią w stronę wież.
```

### `uklad-o3-1.mp3`

```text
[Ola, wiedzma] Najpierw ona, potem ja
[Krystian, narrator] mówisz. Czarodziej uwalnia pannę, a ty w tej samej chwili odlatujesz, zanim zdąży zabrać cię na wieżę.
```

### `koniec-wolna-1.mp3`

```text
[Krystian, narrator] Wracasz pod wieże, ale panny już tam nie ma. Został tylko kurz na deskach. Dokąd poszła? Tego nie wie nikt. Mostek pozostał jako przestroga dla leniwych panien.
```

### `koniec-moc-1.mp3`

```text
[Krystian, narrator] Jesteś najpotężniejszą czarownicą Wrocławia, a jednak każdej nocy słyszysz z wieży szuranie miotły. Moc nie przyniosła ci spokoju.
```

### `koniec-rok-1.mp3`

```text
[Krystian, narrator] Panna zamiata jeszcze rok, ale już bez płaczu. Ostatniego dnia klątwa pęka i panna schodzi z wieży. Ponoć do końca życia pomagała każdemu, kto o to poprosił.
```

### `koniec-zamiana-1.mp3`

```text
[Krystian, narrator] Panna jest wolna, ale to ty budzisz się na mostku z miotłą w ręku. Może właśnie dlatego wrocławianie mówią na niego Mostek Czarownic.
```

### `koniec-ucieczka-1.mp3`

```text
[Krystian, narrator] Masz różdżkę, ale nie umiesz jej używać. Czarodziej bez mocy wciąż szuka cię po Rynku, a panna wciąż zamiata. Ta wersja legendy nie ma szczęśliwego końca.
```

### `koniec-podstep-1.mp3`

```text
[Krystian, narrator] Panna jest wolna, a ty umknęłaś czarodziejowi. Od tamtej nocy nie możesz pokazać się na Rynku, bo starzec wciąż wypatruje cię pod pręgierzem.
```

### `finale-1.mp3`

```text
[Krystian, narrator] A teraz wyobraź sobie, że stoisz na samym mostku, wysoko między wieżami. Pod tobą czerwone dachy Starego Miasta, a dalej całe miasto aż po horyzont.
```

### `finale-2.mp3`

```text
[Krystian, narrator] Tak przez lata widziała Wrocław panna z miotłą.
```

### `reveal-1.mp3`

```text
[Krystian, narrator] Panna z kamienicy miała na imię Tekla. Młoda czarownica to Martynka, a dziwny starzec z Rynku to czarodziej Michał.
```

### `reveal-2.mp3`

```text
[Krystian, narrator] Wszyscy pochodzą z wrocławskiej legendy o Mostku Czarownic, opowiadanej od pokoleń.
```

### `heritage.mp3`

```text
[Krystian, narrator] Legendy żyją, dopóki ktoś je opowiada. Opowiedz tę komuś, kto stoi obok.
```

### `look-up.mp3`

```text
[Krystian, narrator] Wracając, spójrz jeszcze raz na mostek między wieżami: to Mostek Czarownic, zwany też Mostkiem Pokutnic. Zwykle można na niego wejść, godziny sprawdź przy kościele.
```
