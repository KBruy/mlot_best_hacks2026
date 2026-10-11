export const UI = {
  appTitle: 'Żywy Bestiariusz Wrocławia',

  start: {
    subtitle: 'Wybierz legendę i rozpocznij przygodę',
    beginButton: 'Rozpocznij',
    resetHint: 'Odświeżenie strony resetuje grę',
    listPanel: 'Legendy',
    noSelection: 'Wybierz legendę z listy lub mapy',
    aboutLabel: 'O aplikacji',
    welcomeHeadline: 'Odkryj Wrocław na nowo',
    welcomeBody: 'Żywy Bestiariusz to interaktywny spacer śladami wrocławskich legend. Dojdź na miejsce, wysłuchaj historii i podejmuj decyzje — Twoje wybory kształtują zakończenie.',
    welcomeHint: 'Spacery trwają około 10 minut.',
    locationHintDemo: 'Wersja demo umożliwia zagranie z dowolnego miejsca.',
    locationHintLive: 'Gra odblokowuje się po dojściu w pobliże miejsca legendy — zabierz telefon i wyjdź na miasto.',
  },

  demo: {
    on: 'Tryb demo: włączony',
    off: 'Tryb demo: wyłączony',
    gpsWarning: 'GPS niedostępny',
  },

  gps: {
    granted: 'GPS: aktywny',
    denied: 'GPS: brak dostępu',
    unknown: 'GPS: oczekiwanie…',
  },

  loading: {
    message: 'Ładowanie legendy…',
  },

  error: {
    title: 'Błąd połączenia',
    message: 'Nie udało się pobrać historii z serwera.',
    retryButton: 'Spróbuj ponownie',
  },

  scene: {
    decisionHint: (current: number, total: number) => `Decyzja ${current} z ${total}`,
    totalDecisions: 6,
    panelStory: 'Opowieść',
    panelLocation: 'Lokalizacja',
    panelChoices: 'Wybierz odpowiedź',
  },

  consequence: {
    nextButton: 'Dalej',
  },

  ending: {
    hint: 'Koniec legendy',
    continueButton: 'Dalej',
    restartButton: 'Zagraj ponownie',
    scoreLabel: 'Twój wynik',
  },
} as const
