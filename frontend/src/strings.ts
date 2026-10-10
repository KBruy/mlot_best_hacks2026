export const UI = {
  appTitle: 'Żywy Bestiariusz Wrocławia',

  start: {
    subtitle: 'Wybierz legendę i rozpocznij przygodę',
    beginButton: 'Rozpocznij',
    resetHint: 'Odświeżenie strony resetuje grę',
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
  },

  consequence: {
    nextButton: 'Dalej',
  },

  ending: {
    hint: 'Koniec legendy',
    restartButton: 'Zagraj ponownie',
  },
} as const
