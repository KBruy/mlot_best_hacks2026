import type { Story } from './types'

// Mock — zastąpić danymi z backendu (task F3-2)
export const fixtures: Story[] = [
  {
    id: 'krasnolud-piwnic',
    title: 'Krasnolud z Piwnicy Świdnickiej',
    intro: 'Mówią, że w lochach pod Rynkiem mieszka stworzenie starsze od samego miasta. Gdy zegar na ratuszu wybija północ, słychać tupot małych stóp...',
    entry_node_id: 'scena-1',
    characters: [],
    nodes: [
      {
        id: 'scena-1',
        type: 'decision',
        text: 'Stoisz przed wejściem do Piwnicy Świdnickiej. Jest późna noc. Barmanka szepnęła ci, że ostatnio znikają beczki z piwem — żadnych śladów włamania. Tylko mały odcisk buta w kurzu.',
        choices: [
          { id: 'c1-1', text: 'Zejdź do piwnicy sam, z latarnią w dłoni', consequence: 'Schody skrzypią pod każdym krokiem. W ciemności majaczy zarys małej postaci.', next_node_id: 'scena-2' },
          { id: 'c1-2', text: 'Zaczekaj do rana i wróć z miejskim strażnikiem', consequence: 'Strażnik śmieje się z twojej historii — ale w końcu zgadza się zejść razem.', next_node_id: 'scena-2' },
        ],
      },
      {
        id: 'scena-2',
        type: 'decision',
        text: 'W piwnicy natykasz się na krasnoluda siedzącego na beczce. Jest mały, brodaty i wyraźnie zły, że go znaleziono. "Czego chcesz, człowieku?" — pyta skrzypiącym głosem.',
        choices: [
          { id: 'c2-1', text: '"Skradzionego piwa i wyjaśnień"', consequence: 'Krasnolud parska śmiechem. "Skradzione? Ja tu mieszkam od trzystu lat! To wy tu przyszliście!"', next_node_id: 'scena-3' },
          { id: 'c2-2', text: 'Zaproponuj ugodę — zostaw mu beczułkę, niech zostawia resztę', consequence: 'Krasnolud mruży oczy. Propozycja go intryguje. "Jedna beczka miesięcznie? Może..."', next_node_id: 'scena-3' },
        ],
      },
      {
        id: 'scena-3',
        type: 'decision',
        text: 'Rozmowa się przeciąga. Krasnolud okazuje się gadułą — opowiada o czasach gdy Wrocław był jeszcze grodem, nie miastem. Nagle słyszysz kroki na schodach.',
        choices: [
          { id: 'c3-1', text: 'Ukryj krasnoluda za beczkami', consequence: 'Wciskasz małego stwora za największą beczkę. Duka coś niezadowolony, ale się nie rusza.', next_node_id: 'scena-4' },
          { id: 'c3-2', text: 'Wyjdź naprzeciw i odwróć uwagę', consequence: 'Blokujesz wejście. "Tylko sprawdzam zapasy!" — krzyczysz w górę schodów.', next_node_id: 'scena-4' },
        ],
      },
      {
        id: 'scena-4',
        type: 'decision',
        text: 'Niebezpieczeństwo minęło. Krasnolud patrzy na ciebie z nowym szacunkiem. "Nie jesteś głupi jak wyglądasz. Mogę ci coś pokazać — ale musisz obiecać milczenie."',
        choices: [
          { id: 'c4-1', text: 'Obiecaj milczenie i idź za nim', consequence: 'Prowadzi cię korytarzem o którym nikt nie wie. Ściany błyszczą od wilgoci i czegoś jeszcze.', next_node_id: 'scena-5' },
          { id: 'c4-2', text: '"Najpierw powiedz co to jest"', consequence: '"Nieufny. Dobrze." Krasnolud wzrusza ramionami. "Skarb. Stary. Twój, jeśli dotrzymasz słowa."', next_node_id: 'scena-5' },
        ],
      },
      {
        id: 'scena-5',
        type: 'decision',
        text: 'Ukryta komnata. Na środku — skrzynia z monetami bitymi przez Henryka Brodatego. Krasnolud mówi: "Należy do miasta. Zawsze należała. Ale miasto o niej zapomniało." Patrzy na ciebie znacząco.',
        choices: [
          { id: 'c5-1', text: 'Zgłoś znalezisko władzom miasta', consequence: 'Krasnolud kiwa głową powoli. "Wiedziałem że tak zrobisz. Szkoda." Znika w ciemności.', next_node_id: 'scena-6' },
          { id: 'c5-2', text: 'Zostaw skarb tam gdzie jest i zachowaj tajemnicę', consequence: '"Mądrość." Krasnolud uśmiecha się po raz pierwszy. "Chodź, postawię ci piwo."', next_node_id: 'scena-6' },
        ],
      },
      {
        id: 'scena-6',
        type: 'decision',
        text: 'Świta. Stoisz przy wyjściu z piwnicy. Krasnolud zniknął — ale na progu leży mała moneta z orłem piastowskim. Twoja historia z tej nocy.',
        choices: [
          { id: 'c6-1', text: 'Weź monetę i nikomu nie mów', consequence: 'Chowasz ją do kieszeni. Będzie pamiątka — i dowód, że to nie był sen.', next_node_id: 'final-a' },
          { id: 'c6-2', text: 'Zostaw monetę na progu dla następnego', consequence: 'Kładziesz ją z powrotem. Niech inny też dostanie szansę na spotkanie.', next_node_id: 'final-b' },
        ],
      },
      {
        id: 'final-a',
        type: 'ending',
        title: 'Strażnik Tajemnicy',
        text: 'Moneta wylądowała w szufladzie na dnie komody. Przez lata nikt jej nie widział. Ale ilekroć wracasz do Piwnicy Świdnickiej, barmanka mówi że piwo ostatnio znika rzadziej. Krasnolud dotrzymał słowa.',
      },
      {
        id: 'final-b',
        type: 'ending',
        title: 'Łańcuch Opowieści',
        text: 'Tydzień później słyszysz w gospodzie historię o jakimś kupcu, który znalazł monetę przy wejściu do piwnicy i spędził tam całą noc rozmawiając z kimś małym i brodatym. Uśmiechasz się do swojego kufla.',
      },
    ],
  },
  {
    id: 'czarna-woda',
    title: 'Czarna Woda pod Mostem Tumskim',
    intro: 'Stary rybak twierdzi że w Odrze pod Mostem Tumskim mieszka coś, co śpiewa po łacinie w bezksiężycowe noce. Nikt mu nie wierzy. Nikt poza tobą.',
    entry_node_id: 'cw-1',
    characters: [],
    nodes: [
      {
        id: 'cw-1',
        type: 'decision',
        text: 'Stoisz na Moście Tumskim o północy. Woda jest czarna jak smoła. I rzeczywiście — coś śpiewa. Głos jest piękny i nieludzki zarazem.',
        choices: [
          { id: 'cw1-1', text: 'Zejdź na brzeg i podejdź bliżej', consequence: 'Kamienie są śliskie od mchu. Śpiew staje się głośniejszy i nagle — urywa się.', next_node_id: 'cw-2' },
          { id: 'cw1-2', text: 'Odpowiedz śpiewem — zaśpiewaj cokolwiek', consequence: 'Twój głos kruszy ciszę. Po chwili śpiew z wody odpowiada, jakby pytając.', next_node_id: 'cw-2' },
        ],
      },
      {
        id: 'cw-2',
        type: 'decision',
        text: 'Z wody wyłania się twarz — nie ludzka, zbyt blada, zbyt symetryczna. Stworzenie patrzy na ciebie bez mrugania. "Dawno nikt nie przyszedł" — mówi po polsku z dziwnym akcentem.',
        choices: [
          { id: 'cw2-1', text: '"Kim jesteś?"', consequence: '"Byłam tu przed mostem. Będę tu po moście. Teraz — jestem po prostu zmęczona."', next_node_id: 'cw-3' },
          { id: 'cw2-2', text: '"Czego chcesz?"', consequence: '"Chcę? Nic. Śpiewam bo inaczej zapomnę słowa. A słowa są wszystkim co mi zostało."', next_node_id: 'cw-3' },
        ],
      },
      {
        id: 'cw-3',
        type: 'decision',
        text: 'Stworzenie opowiada o mieście sprzed wieków — o murach których już nie ma, o ludziach których imiona zatarło powietrze. Słuchasz godzinę, może dwie.',
        choices: [
          { id: 'cw3-1', text: 'Zapytaj o konkretne imię — kogoś zapomnianego', consequence: 'Milknie. Potem wolno wymawia imię którego nie słyszałeś nigdy. Ale brzmi jak prawdziwe.', next_node_id: 'cw-4' },
          { id: 'cw3-2', text: 'Opowiedz jej coś o dzisiejszym Wrocławiu', consequence: 'Słucha z zamkniętymi oczami. "Wieże nadal stoją" — mówi w końcu. "Dobrze."', next_node_id: 'cw-4' },
        ],
      },
      {
        id: 'cw-4',
        type: 'decision',
        text: 'Zaczyna świtać. Stworzenie zaczyna się cofać w wodę. "Wróć — jeśli chcesz słuchać. Ale nie przyprowadzaj nikogo."',
        choices: [
          { id: 'cw4-1', text: '"Wrócę sam"', consequence: '"Wiem." I znika. Masz wrażenie że wiedziała to zanim zapytała.', next_node_id: 'cw-5' },
          { id: 'cw4-2', text: 'Milczysz — nie składasz obietnic', consequence: 'Patrzy na ciebie długo. "Uczciwy." Kiwa głową i odpływa w ciemność.', next_node_id: 'cw-5' },
        ],
      },
      {
        id: 'cw-5',
        type: 'decision',
        text: 'Wracasz do domu gdy miasto się budzi. W głowie masz imię które wymówiła — i nagle wiesz gdzie szukać. W archiwum katedralnym, w piwnicy, w skrzyni która nigdy nie była katalogowana.',
        choices: [
          { id: 'cw5-1', text: 'Idź do archiwum teraz, zanim zapomnisz', consequence: 'Archiwariusz jest zaskoczony o tak wczesnej porze. Ale wpuszcza cię. I rzeczywiście — jest skrzynia.', next_node_id: 'cw-6' },
          { id: 'cw5-2', text: 'Wróć do domu i spisz wszystko co pamiętasz', consequence: 'Piszesz trzy godziny bez przerwy. Kiedy kończysz — masz gotową historię której nikt nie zna.', next_node_id: 'cw-6' },
        ],
      },
      {
        id: 'cw-6',
        type: 'decision',
        text: 'Wieczorem wracasz na Most Tumski. Woda jest spokojna. Czekasz godzinę. Śpiewu nie ma. Ale na powierzchni wody unosi się coś małego — złożony kawałek pergaminu.',
        choices: [
          { id: 'cw6-1', text: 'Wyciągnij pergamin i przeczytaj', consequence: 'Jest zapisany w języku którego nie znasz. Ale jedno słowo rozumiesz — twoje imię.', next_node_id: 'final-cw-a' },
          { id: 'cw6-2', text: 'Zostaw pergamin na wodzie', consequence: 'Odpływa powoli pod most. Masz wrażenie że tak powinno być.', next_node_id: 'final-cw-b' },
        ],
      },
      {
        id: 'final-cw-a',
        type: 'ending',
        title: 'Imię w Starym Języku',
        text: 'Pergamin trafił do gablotki nad biurkiem. Nikt kto go widzi nie pyta skąd pochodzi — jakby bali się odpowiedzi. Ale w bezksiężycowe noce, gdy mija Most Tumski, słyszysz śpiew. I teraz wiesz że to dla ciebie.',
      },
      {
        id: 'final-cw-b',
        type: 'ending',
        title: 'Rzeka Pamięta',
        text: 'Odra zabrała pergamin tam gdzie zabrała wszystko inne — w głąb, w ciemność, w ciszę. Ale ty wiesz teraz że rzeka pamięta więcej niż ludzie. I że czasem warto słuchać wody zamiast mówić.',
      },
    ],
  },
]
