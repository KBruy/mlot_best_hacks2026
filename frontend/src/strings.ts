export const UI = {
  appTitle: 'Żywy Bestiariusz Wrocławia',

  start: {
    subtitle: 'Wybierz legendę i rozpocznij przygodę',
    beginButton: 'Rozpocznij',
    resetHint: 'Odświeżenie strony resetuje grę',
    listPanel: 'Legendy',
    noSelection: 'Wybierz legendę z listy lub mapy',
  },

  demo: {
    on: 'Tryb demo: włączony',
    off: 'Tryb demo: wyłączony',
    // TODO: po otrzymaniu kontraktu danych — podpiąć tu Street View pierwszej lokalizacji legendy
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
    restartButton: 'Zagraj ponownie',
  },
} as const
