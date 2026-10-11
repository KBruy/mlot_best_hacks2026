# Narracja „Kamiennej głowy”: przypisanie głosów

Kto czyta który akapit legendy. Każdy plik poniżej odpowiada jednemu `audio_url` w `content/kamienna-glowa.json` (jeden akapit albo jeden wariant `if`). Teksty opcji nie są czytane. Próbki głosów: [NAGRANIA.md](NAGRANIA.md), profile postaci: `characters.yaml`. Generowanie, przycinanie i karaoke działają tak samo jak dla „Mostku Czarownic”: [NARRACJA.md](NARRACJA.md#generowanie).

## Generowanie

Z katalogu `voice-service/`:

```bash
uv run python narrate.py --story kamienna-glowa --check       # spójność skryptów z legendą (szybko, bez modeli)
uv run python narrate.py --story kamienna-glowa warsztat-1    # próba na jednym pliku
uv run python narrate.py --story kamienna-glowa               # wszystkie brakujące pliki
uv run python narrate.py --story kamienna-glowa --force kolega-1   # nowe podejście do złego pliku
```

Wyniki: WAV w `voice-service/outputs/kamienna-glowa/`, MP3 i znaczniki czasu słów w `frontend/public/audio/kamienna-glowa/`.

## Zasady

- Całą narrację (druga osoba, „ty”) czyta **narrator**: `[Krystian, narrator]`.
- Kwestie w dialogach czytają postacie. Nie trzeba nowych próbek ani profili:

  | Postać | Skrypt | Próbka |
  | --- | --- | --- |
  | czeladnik (gracz) | `[Krystian, kawaler]` | `krystian_kawaler.wav` |
  | mistrz złotnik | `[Andrzej, ojciec]` | `andrzej_ojciec.wav` |
  | drugi czeladnik (rywal) | `[Adrian, czeladnik]` | `adrian_neutral.wav` |
  | córka mistrza | `[Ola, panna]` | `ola_panna.wav` |
  | ksiądz | `[Adrian, starzec]` | `adrian_starzec.wav` |

  Wtrącenia typu „grzmi pryncypał” czyta narrator.
- Fragmenty skryptu składają się dokładnie na słowa tekstu z legendy (bez myślników dialogowych), więc napisy i nagranie się zgadzają.
- Legenda powtarza niektóre akapity pod różnymi plikami (np. „Córkę zamyka pod strażą…” w `mistrz-o*-2`, pożar w `odmowa-o1-*`, `ofiara-o1-*` i `rozmowa-o1-*`). Identyczne kwestie trafiają do cache, więc generują się raz.
- Razem **95 plików**, w tym 11 z dialogiem (kilka głosów w jednym pliku).
- Bardzo krótkie kwestie warto odsłuchać, bo model bywa na nich niestabilny: „Do wiosny.” (`szlak-o2-1`), „mówi cicho.” (`ofiara-1`), „pyta chłodno.” (`rozmowa-2`), „Wrócę bogaty.” (`przysiega-o1-1`).

## Skrypty

### `intro-1-plac.mp3`

```text
[Krystian, narrator] Stań na placu, twarzą do katedry, i spójrz wysoko na jej wieże. Gdzieś w murze, w małym okienku, tkwi kamienna twarz.
```

### `intro-1-ogolny.mp3`

```text
[Krystian, narrator] Rozejrzyj się za wieżami katedry na Ostrowie Tumskim. Gdzieś wysoko w murze, w małym okienku, tkwi kamienna twarz.
```

### `intro-2.mp3`

```text
[Krystian, narrator] Wrocławianie od wieków opowiadają, czyja to twarz i dlaczego nie może się stamtąd ruszyć.
```

### `intro-3.mp3`

```text
[Krystian, narrator] Wpisz numer i Enter, a q kończy grę.
```

### `warsztat-1.mp3`

```text
[Krystian, narrator] Jesteś czeladnikiem w warsztacie jednego z najpotężniejszych wrocławskich złotników. Córka mistrza mogłaby poślubić każdego patrycjusza w mieście, lecz ku twojemu zdumieniu i radości, to właśnie na ciebie patrzy z czułością, którą odwzajemniasz.
```

### `warsztat-2.mp3`

```text
[Krystian, narrator] Mistrz nie wie o niczym i nie byłby zadowolony z jej wyboru. W warsztacie pracuje obok ciebie jeszcze jeden czeladnik, który też często zerka w stronę mistrzowskiego domu.
```

### `warsztat-o1-1.mp3`

```text
[Krystian, narrator] Całą noc pracujesz w tajemnicy przed mistrzem. Gdy nad ranem pierścień jest wreszcie gotowy i jej go wręczasz, ona w zamian obdarowuje cię własnoręcznie wyhaftowaną chustką.
```

### `warsztat-o2-1.mp3`

```text
[Krystian, narrator] Zbierasz się na odwagę i stajesz przed mistrzem. Serce wali ci tak, że ledwie słyszysz własne słówa.
```

### `warsztat-o3-1.mp3`

```text
[Krystian, narrator] Siadacie razem przy warsztacie. Szybko orientujesz się, że drugi czeladnik od dawna wzdycha do córki mistrza i z rosnącą podejrzliwością wypytuje, gdzie spędzasz wieczory.
```

### `ogrod-1.mp3`

```text
[Krystian, narrator] Wieczorami wymykacie się do ogrodu, podczas gdy opiekunka dziewczyny dba o to, by nikt was nie nakrył. Srebrny pierścień lśni na jej dłoni, a schowana przy tobie chustka pachnie lawendą.
```

### `ogrod-2.mp3`

```text
[Krystian, narrator] Wiesz jednak, że stąpacie po kruchym lodzie - wasz sekret znają tylko zaufana piastunka oraz ten drugi, uważnie obserwujący cię czeladnik.
```

### `ogrod-o1-1.mp3`

```text
[Krystian, narrator] Pilnujesz się na każdym kroku, lecz zazdrosny czeladnik od dawna patrzył i w końcu zdradza wasz sekret mistrzowi.
```

### `ogrod-o1-2.mp3`

```text
[Krystian, narrator] Tego samego wieczoru złotnik osobiście zakrada się do ogrodu. Gdy was nakrywa, wpada w furię, wyrzuca cię za bramę. Córce zapowiada zaś, że nie opuści domu bez straży aż do dnia, w którym on sam wybierze jej męża.
```

### `ogrod-o2-1.mp3`

```text
[Krystian, narrator] Naiwnie ufasz rywalowi i zdradzasz mu swój sekret. Ten z fałszywym uśmiechem natychmiast wydaje cię mistrzowi.
```

### `ogrod-o2-2.mp3`

```text
[Krystian, narrator] Wieczorem wściekły złotnik osobiście wkracza do ogrodu. Z krzykiem i laską w dłoni wyrzuca cię z domu. Córce grozi strażą aż do dnia, w którym sam wybierze jej męża.
```

### `ogrod-o3-1.mp3`

```text
[Krystian, narrator] List wpada w ręce zazdrosnego czeladnika, który zamiast przekazać go adresatce, zanosi go prosto do mistrza.
```

### `ogrod-o3-2.mp3`

```text
[Krystian, narrator] Wieczorem wściekły złotnik osobiście wkracza do ogrodu. Z krzykiem i laską w dłoni wyrzuca cię z domu. Córce grozi strażą aż do dnia, w którym sam wybierze jej męża.
```

### `mistrz-1.mp3`

```text
[Krystian, narrator] Mistrz słucha w milczeniu, a jego twarz niebezpiecznie ciemnieje z gniewu. Za drzwiami słychać cichy szmer – to drugi czeladnik, który podsłuchuje z wyraźnym zadowoleniem.
```

### `mistrz-2.mp3`

```text
[Andrzej, ojciec] Ty? Nędzny czeladnik ośmiela się prosić o rękę mojej córki?!
[Krystian, narrator] grzmi pryncypał, a jego dłoń gwałtownie zaciska się na rękojeści ciężkiej laski.
```

### `mistrz-o1-1.mp3`

```text
[Krystian, kawaler] Kocham ją i nie ustąpię.
[Krystian, narrator] mówisz. Mistrz wymachuje laską i wyprasza cię z domu, wrzeszcząc.
```

### `mistrz-o1-2.mp3`

```text
[Krystian, narrator] Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `mistrz-o2-1.mp3`

```text
[Andrzej, ojciec] Czas? Ona ma męża wtedy, kiedy ja zdecyduję!
[Krystian, narrator] krzyczy mistrz i przegania cię laską.
```

### `mistrz-o2-2.mp3`

```text
[Krystian, narrator] Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `mistrz-o3-1.mp3`

```text
[Krystian, narrator] Mistrz robi się purpurowy. Biegnie do ogrodu, wymachując laską, a ciebie przegania z domu, zanim zdążysz cokolwiek dodać.
```

### `mistrz-o3-2.mp3`

```text
[Krystian, narrator] Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `kolega-1.mp3`

```text
[Adrian, czeladnik] Wymykasz się dokądś po zmroku, prawda?
[Krystian, narrator] pyta twój rywal, a na jego twarz wypełza nieszczery, lodowaty uśmiech, podczas gdy oczy pozostają czujne.
[Adrian, czeladnik] Nie musisz się ukrywać, przecież mnie możesz zaufać.
```

### `kolega-o1-1.mp3`

```text
[Krystian, narrator] Śmiejesz się i zmieniasz temat. Czeladnik jednak nie daje za wygraną i cierpliwie czeka na dogodną okazję. Pewnego wieczoru śledzi cię aż do ogrodu, po czym natychmiast sprowadza mistrza.
```

### `kolega-o1-2.mp3`

```text
[Krystian, narrator] Mistrz wrzeszczy i wymachując laską przegania cię z ogrodu. Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `kolega-o2-1.mp3`

```text
[Krystian, narrator] Mówisz wszystko, bo uważasz go za przyjaciela. Czeladnik kiwa głową i tego samego dnia idzie do mistrza.
```

### `kolega-o2-2.mp3`

```text
[Krystian, narrator] Mistrz wrzeszczy i wymachując laską przegania cię z domu. Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `kolega-o3-1.mp3`

```text
[Krystian, narrator] Poniesiony gniewem tracisz nad sobą kontrolę i w kłótni wykrzykujesz o wiele więcej, niż zamierzałeś. Twój rywal z satysfakcją łowi każde nierozważne słowo, a zanim zdążysz ochłonąć i pożałować swojej porywczości, mistrz już zna wasz sekret.
```

### `kolega-o3-2.mp3`

```text
[Krystian, narrator] Mistrz wrzeszczy i wymachując laską przegania cię z domu. Córkę zamyka pod strażą aż do dnia, w którym sam wybierze jej męża.
```

### `przysiega-1.mp3`

```text
[Krystian, narrator] Stajesz na środku mostu. To tędy opuszcza się miasto. Po raz ostatni patrzysz na Wrocław, zanim na zawsze zniknie ci z oczu za zakrętem rzeki.
```

### `przysiega-2-pierscien.mp3`

```text
[Krystian, narrator] Wiesz, że w tamtym ogrodzie na zawsze zostało twoje szczęście i ukochana z pierścieniem na palcu. Tobie na pamiątkę została jedynie schowana w kieszeni chustka.
```

### `przysiega-2-prosba.mp3`

```text
[Krystian, narrator] Wiesz, że mistrz nigdy ci nie wybaczy, że ubogi czeladnik śmiał prosić o jego córkę.
```

### `przysiega-2-zazdrosc.mp3`

```text
[Krystian, narrator] Świadomość, że wydał cię człowiek, którego uważałeś za przyjaciela, dodaje tej porażce jedynie goryczy.
```

### `przysiega-3.mp3`

```text
[Krystian, narrator] Opuszczasz miasto, uciekając przed groźbami mistrza. Jednak zanim za tobą zniknie ostatni wrocławski dach, musisz złożyć sobie obietnicę.
```

### `przysiega-o1-1.mp3`

```text
[Krystian, kawaler] Wrócę bogaty.
[Krystian, narrator] mówisz cicho do rzeki.
[Krystian, kawaler] Tak bogaty, że mistrz sam poprosi mnie o jej rękę.
```

### `przysiega-o1-2.mp3`

```text
[Krystian, narrator] Odwracasz się i odchodzisz z miasta. Nie masz przy sobie ani uncji złota, ale masz jasny cel.
```

### `przysiega-o2-1.mp3`

```text
[Krystian, kawaler] Obaj tego pożałują.
[Krystian, narrator] szepczysz, zaciskając pięści na poręczy mostu.
```

### `przysiega-o2-2.mp3`

```text
[Krystian, narrator] Odwracasz się i odchodzisz z miasta. Nie masz przy sobie ani uncji złota, ale masz jasny cel.
```

### `przysiega-o3-1.mp3`

```text
[Krystian, narrator] Nie składasz żadnych przysiąg. Rzucasz miastu ostatnie spojrzenie i odwracasz się w stronę drogi.
```

### `przysiega-o3-2.mp3`

```text
[Krystian, narrator] Odchodzisz z Wrocławia w milczeniu – nie masz ani uncji złota, ani jasnego celu, a twoim jedynym majątkiem jest ukryta w kieszeni chustka
```

### `szlak-1.mp3`

```text
[Krystian, narrator] Przez długie miesiące tułasz się po okolicznych miasteczkach i wsiach. Nikt nie ufa przybyszowi znikąd, więc nikt nie chce dać ci pracy. Zbliża się sroga zima, a ty wciąż nie masz dachu nad głową.
```

### `szlak-2.mp3`

```text
[Krystian, narrator] Wtedy właśnie na twojej drodze staje banda zbójców. Nie masz przy sobie absolutnie niczego, czym mógłbyś okupić swoje życie. Twój los wisi na włosku: mogą cię zabić na miejscu albo przyjąć do swojej watahy
```

### `szlak-o1-1.mp3`

```text
[Krystian, narrator] Dołączasz do bandy. Napadasz na podróżnych kupców i wieśniaków niosących sakwy ze złotem, a przed snem powtarzasz sobie: to wszystko dla niej.
```

### `szlak-o1-2.mp3`

```text
[Krystian, narrator] Obiecujesz Bogu, że gdy połączysz się z ukochaną, złożysz do kościoła ogromną ofiarę. Mijają lata, a imię rozbójnika powtarza się na całym szlaku z Wrocławia do Pragi.
```

### `szlak-o2-1.mp3`

```text
[Krystian, kawaler] Do wiosny.
[Krystian, narrator] mówisz. Ale wiosną łup jest zbyt dobry, a drogi powrotnej nie ma.
```

### `szlak-o2-2.mp3`

```text
[Krystian, narrator] Obiecujesz Bogu, że gdy połączysz się z ukochaną, złożysz do kościoła ogromną ofiarę. Mijają lata, a imię rozbójnika powtarza się na całym szlaku z Wrocławia do Pragi.
```

### `szlak-o3-1.mp3`

```text
[Krystian, narrator] Nie zostawiasz świadków, nie okazujesz litości, dlatego bandyci szybko zaczynają cię słuchać.
```

### `szlak-o3-2.mp3`

```text
[Krystian, narrator] Obiecujesz Bogu, że gdy połączysz się z ukochaną, złożysz do kościoła ogromną ofiarę. Mijają lata, a imię rozbójnika powtarza się na całym szlaku z Wrocławia do Pragi.
```

### `powrot-1.mp3`

```text
[Krystian, narrator] Minęło kilkanaście lat. Zatrzymujesz się na Ostrowie Tumskim, w cieniu katedry. Bujna broda sprawia, że nikt w mieście cię nie poznaje. Jesteś teraz bezwzględnym przywódcą zbójeckiej bandy, a w twoich sakwach wreszcie ciąży upragnione złoto.
```

### `powrot-2-bogactwo.mp3`

```text
[Krystian, narrator] Przysiągłeś sobie kiedyś, że wrócisz tak bogaty, iż mistrz sam poprosi cię o poślubienie jego córki. Dziś masz w sakwach dość złota, żeby dosłownie kupić jej rękę.
```

### `powrot-2-zemsta.mp3`

```text
[Krystian, narrator] Przysiągłeś zemstę i nie zapomniałeś o niej ani na jeden dzień.
```

### `powrot-2-cisza.mp3`

```text
[Krystian, narrator] Wróciłeś, sam do końca nie wiedząc po co: może szukasz odkupienia win, a może po prostu chcesz jeszcze raz ujrzeć jej twarz.
```

### `powrot-3.mp3`

```text
[Krystian, narrator] Mistrz wciąż mieszka w swojej kamienicy na Rynku, ale to katedra wznosi się tuż przed tobą, a przecież obiecałeś Bogu złożyć ofiarę za swoje czyny.
```

### `powrot-o1-1.mp3`

```text
[Krystian, narrator] Zostawiasz katedrę za plecami i idziesz na Rynek. Stajesz przed dawnym mistrzem i oznajmiasz, że jesteś tym samym chłopcem, którego przed laty przegnał.
```

### `powrot-o2-1.mp3`

```text
[Krystian, narrator] Wchodzisz do katedry z sakwami. Zatrzymuje cię ksiądz, zaciekawiony ciężarem.
```

### `powrot-o3-1.mp3`

```text
[Krystian, narrator] Idziesz na Rynek i zatrzymujesz się przy znajomym ogrodzie. Czekasz tam do wieczora, zupełnie jak za dawnych lat, kiedy oboje musieliście ukrywać się przed światem.
```

### `odmowa-1.mp3`

```text
[Krystian, narrator] Mistrz, całkowicie zaślepiony widokiem złota, sam biegnie po córkę do jej pokoju. Ona jednak słyszała waszą rozmowę, a gdy uświadamia sobie, skąd pochodzi ten majątek, patrzy na ciebie z odrazą.
```

### `odmowa-2.mp3`

```text
[Ola, panna] Nie chcę ani ciebie, ani bogactwa zrabowanego innym.
[Krystian, narrator] mówi twardo. Nie potrafisz przyjąć tej odmowy. Wpadając w gniew, zrzucasz całą winę na dawnego pryncypała i warczysz w jego stronę:
[Krystian, kawaler] Jeszcze pożałujesz swojej decyzji sprzed lat!
```

### `odmowa-o1-1.mp3`

```text
[Krystian, narrator] Tej samej nocy podkładasz ogień pod jego kamienicę na Rynku. Płomienie pną się po ścianach, a ty biegniesz przez Most Piaskowy na Ostrów Tumski i wspinasz się na wieżę katedry.
```

### `odmowa-o1-2.mp3`

```text
[Krystian, narrator] Wychylasz się przez małe okienko i patrzysz na pożar. Kamienica spłonie prawie cała. Zadowolony chcesz się cofnąć, ale głowa nie ruszy się z miejsca. Mur zaciska się wokół niej coraz mocniej.
```

### `odmowa-o1-3.mp3`

```text
[Krystian, narrator] Szarpiesz się i krzyczysz, ale szczelina okienka nie chce cię wypuścić. Zostajesz tam na zawsze.
```

### `odmowa-o2-1.mp3`

```text
[Krystian, narrator] Kłaniasz się mistrzowi, odwracasz się i wychodzisz z kamienicy. Nikt nie próbuje cię zatrzymać.
```

### `odmowa-o3-1.mp3`

```text
[Krystian, narrator] Wysypujesz całe przyniesione złoto na stół i z ciężkim westchnieniem padasz na kolana. Ona milczy, a dawny mistrz patrzy na ciebie z nieukrywaną zgrozą.
```

### `ofiara-1.mp3`

```text
[Krystian, narrator] Składasz w katedrze zrabowane złoto. Ksiądz długo przygląda się sakwom, a potem odsuwa je od siebie.
[Adrian, starzec] Takiej ofiary Bóg nie przyjmie.
[Krystian, narrator] mówi cicho.
[Adrian, starzec] Na tym złocie nadal schnie cudza krew.
```

### `ofiara-2.mp3`

```text
[Krystian, narrator] Wychodzisz na plac. Złoto ciąży ci bardziej niż przedtem.
```

### `ofiara-o1-1.mp3`

```text
[Krystian, narrator] Mistrz i jego córka odmawiają ci, wiedząc, skąd masz złoto. Zaślepiony, nie wybaczasz.
```

### `ofiara-o1-2.mp3`

```text
[Krystian, narrator] Tej samej nocy podkładasz ogień pod jego kamienicę na Rynku. Płomienie pną się po ścianach, a ty biegniesz przez Most Piaskowy na Ostrów Tumski i wspinasz się na wieżę katedry.
```

### `ofiara-o1-3.mp3`

```text
[Krystian, narrator] Wychylasz się przez małe okienko i patrzysz na pożar. Kamienica spłonie prawie cała. Zadowolony chcesz się cofnąć, ale głowa nie ruszy się z miejsca. Mur zaciska się wokół niej coraz mocniej.
```

### `ofiara-o1-4.mp3`

```text
[Krystian, narrator] Szarpiesz się i krzyczysz, ale szczelina okienka nie chce cię wypuścić. Zostajesz tam na zawsze.
```

### `ofiara-o2-1.mp3`

```text
[Krystian, narrator] Klękasz, wyznajesz wszystko i sam prosisz o to, żeby wezwano straż miejską.
```

### `ofiara-o3-1.mp3`

```text
[Krystian, narrator] Zdejmujesz płaszcz herszta i prosisz o miejsce przy klasztornej furcie.
```

### `rozmowa-1.mp3`

```text
[Krystian, narrator] Z domu wychodzi ona. Jest widocznie starsza, ale od razu poznaje twoje spojrzenie, kiedy wyciągasz z kieszeni starą, wyhaftowaną chustkę. Przez krótką chwilę znów dostrzegasz w niej tamtą dziewczynę sprzed lat
```

### `rozmowa-2.mp3`

```text
[Krystian, narrator] Zaraz potem jednak mruży podejrzliwie oczy.
[Ola, panna] To ty jesteś tym zbójem z gościńca do Pragi?
[Krystian, narrator] pyta chłodno.
```

### `rozmowa-3.mp3`

```text
[Ola, panna] Cały Wrocław o tobie słyszał.
```

### `rozmowa-o1-1.mp3`

```text
[Krystian, narrator] Odsuwa się od ciebie z odrazą. W tej chwili zrozumiałeś, że nie odzyskasz niczego, co straciłeś.
```

### `rozmowa-o1-2.mp3`

```text
[Krystian, narrator] Tej samej nocy podkładasz ogień pod jego kamienicę na Rynku. Płomienie pną się po ścianach, a ty biegniesz przez Most Piaskowy na Ostrów Tumski i wspinasz się na wieżę katedry.
```

### `rozmowa-o1-3.mp3`

```text
[Krystian, narrator] Wychylasz się przez małe okienko i patrzysz na pożar. Kamienica spłonie prawie cała. Zadowolony chcesz się cofnąć, ale głowa nie ruszy się z miejsca. Mur zaciska się wokół niej coraz mocniej.
```

### `rozmowa-o1-4.mp3`

```text
[Krystian, narrator] Szarpiesz się i krzyczysz, ale szczelina okienka nie chce cię wypuścić. Zostajesz tam na zawsze.
```

### `rozmowa-o2-1.mp3`

```text
[Krystian, narrator] Chowasz chustkę, kiwasz głową w ciemności i znikasz w uliczkach, zanim zdąży zawołać straż.
```

### `rozmowa-o3-1.mp3`

```text
[Krystian, narrator] Mówisz cicho i długo. Ona nie odpowiada, tylko patrzy, a potem zamyka furtkę.
```

### `koniec-glowa-1.mp3`

```text
[Krystian, narrator] Wrocławianie powtarzają, że do dziś w katedralnej wieży widać twarz zbójnika wpatrzonego w ogień, który sam podłożył. Jego skamieniała głowa pozostała tam na zawsze, służąc jako przestroga dla wszystkich, którzy w imię miłości gotowi są krzywdzić innych.
```

### `koniec-odejscie-1.mp3`

```text
[Krystian, narrator] Odchodzisz z Wrocławia tak samo cicho, jak do niego wróciłeś. Nikt nie wie, dokąd ostatecznie udał się słynny zbój z bujną brodą, a w oknie wieży katedry nie ma żadnej skamieniałej twarzy.
```

### `koniec-ofiara-1.mp3`

```text
[Krystian, narrator] Mistrz nie przyjmuje twojego złota, a ona nie przyjmuje ciebie. Złoto trafia w końcu do kościoła, ale w kronikach nikt nie zapisał, czy Bóg je przyjął.
```

### `koniec-sad-1.mp3`

```text
[Krystian, narrator] Straż prowadzi cię na ratusz, a z gościńca do Pragi ludzie wreszcie mogą odetchnąć. Kamienna głowa w oknie wieży to tylko legenda: ty swoją karę odbyłeś zwyczajnie, jak każdy zbójca.
```

### `koniec-pokuta-1.mp3`

```text
[Krystian, narrator] Do końca życia pomagasz przy klasztornej furcie i nie wspominasz nikomu, kim byłeś. Ponoć w oknie wieży nigdy nie pojawiła się żadna głowa.
```

### `koniec-ucieczka-1.mp3`

```text
[Krystian, narrator] Uciekasz z całym łupem, ale na gościńcu do Pragi czekają już na ciebie inni zbóje. Złoto, na które pracowałeś kilkanaście lat, rozchodzi się w kilka nocy.
```

### `finale-1.mp3`

```text
[Krystian, narrator] A teraz zadrzyj głowę i poszukaj wzrokiem okienka w wieży katedry. Według legendy tkwi w nim do dziś kamienna twarz, która patrzy w stronę Rynku.
```

### `finale-2.mp3`

```text
[Krystian, narrator] Tak przez wieki patrzył na Wrocław zbójnik, który chciał kupić miłość.
```

### `reveal-1.mp3`

```text
[Krystian, narrator] Legenda nie podaje imion. Był młody czeladnik bogatego złotnika, jego ukochana, córka mistrza, jej opiekunka i drugi czeladnik, który z zazdrości wydał sekret. Czeladnik został rozbójnikiem, a po latach wrócił do Wrocławia.
```

### `reveal-2.mp3`

```text
[Krystian, narrator] Wszyscy pochodzą z wrocławskiej legendy o kamiennej głowie, opowiadanej od pokoleń.
```

### `heritage.mp3`

```text
[Krystian, narrator] Legendy żyją, dopóki ktoś je opowiada. Opowiedz tę komuś, kto stoi obok.
```

### `look-up.mp3`

```text
[Krystian, narrator] Wracając, spójrz jeszcze raz na wieże katedry: gdzieś w murze tkwi kamienna głowa. Poszukaj okienka, w którym według legendy utknął zbójnik.
```
