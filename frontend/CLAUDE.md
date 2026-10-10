# CLAUDE.md — Frontend

## Kontekst

Frontend PWA do hackathonowego projektu "Żywy Bestiariusz Wrocławia" — tekstowa gra RPG z legendami wrocławskimi.
Pełny scope i kontrakt danych w `../CLAUDE.md` i `../SCOPE_V0.md`. Ten plik zawiera wyłącznie decyzje frontendowe.

> **Uwaga:** Root CLAUDE.md mówi "zwykły CSS", ale frontend używa **Tailwind CSS** — pozwala szybciej wdrożyć
> tematyzację i jest spójny z planowanym stylem Helltaker. Nie dodawaj innych bibliotek CSS.

> **Struktura i flow są wstępne.** Architektura ekranów, podział komponentów i przepływ danych mogą się zmienić
> w zależności od decyzji backendu (kształt API, format danych, endpointy). Przed implementacją sprawdź
> aktualny kontrakt z zespołem i `docs/INTEGRATIONS.md`.

> **Paleta kolorów i styl wizualny nie są jeszcze ustalone.** Wartości kolorów, motyw Helltaker i konkretne
> zmienne CSS w tym pliku są propozycją roboczą — nie implementuj ich jako finalnych bez potwierdzenia
> z zespołem. Docelową paletę wpisz do `docs/DECISIONS.md` gdy zostanie zatwierdzona.

## Stack

- Vite + React + TypeScript
- Tailwind CSS z CSS Variables dla motywów (klasy na `<body>`)
- Stan: `useReducer` + `Context` — bez Zustand i zewnętrznych store'ów
- Bez React Router — nawigacja przez zmianę stanu gry
- Bez dodatkowych bibliotek UI, animacji i ikony z localStorage

## Zasady jakości kodu (definicja ukończenia)

Kod uznajemy za gotowy gdy spełnia **wszystkie** poniższe zasady. To nie są preferencje — to warunki odbioru.

### 0. Lintery — obowiązkowe
Projekt używa **oxlint** (już skonfigurowany w `.oxlintrc.json`). Zasady:
- Przed każdym commitem uruchom `npm run lint` i napraw **wszystkie** błędy
- Warningi traktuj jak błędy — nie commituj kodu z warningami
- Nie wyłączaj reguł przez `// eslint-disable` ani `// oxlint-disable` bez wyraźnego powodu
- Jeśli reguła przeszkadza — przedyskutuj zmianę w `.oxlintrc.json`, nie obchodź jej inline

W przyszłości można rozważyć dodanie `prettier` do formatowania — decyzja do ustalenia z zespołem.

### 1. Czytelność
Każda linia kodu powinna być zrozumiała bez komentarza. Dobre nazwy zmiennych i funkcji zastępują dokumentację.
Unikaj zagnieżdżonych trójników, długich łańcuchów `.then()` i anonimowych callbacków tam gdzie ma to nazwę.

### 2. Elastyczność przez propsy
Każdy komponent przyjmuje propsy dla wszystkich zmiennych wartości (kolor, rozmiar, tekst, callback).
Nie hardkoduj wartości wewnątrz komponentu jeśli może ją przekazać rodzic.

```tsx
// ŹLE
<Button className="bg-red-600 text-lg">Dalej</Button>

// DOBRZE
<Button variant="primary" size="lg" onClick={onNext}>Dalej</Button>
```

### 3. Architektura Bulletproof React
Kod organizujemy wg feature-based structure. Każdy ekran/feature to osobny folder z własną logiką.
Komponenty dzielimy na trzy poziomy:
- **`shared/`** — komponenty wielokrotnego użytku, niezależne od domeny
- **`components/`** — komponenty specyficzne dla feature'a
- **`screens/`** — pliki widoków (tylko kompozycja komponentów)

### 4. Reguła ekranów — zero surowego Tailwinda w screen-files
Pliki w `screens/` są **wyłącznie kompozycją** gotowych komponentów.
Żadnych długich ciągów klas Tailwinda w `SceneScreen.tsx`, `EndingScreen.tsx` itp.
Każdy blok layoutu i stylu musi być wyciągnięty do nazwanego komponentu.

```tsx
// ŹLE — screen z surowym Tailwindem
export function SceneScreen() {
  return (
    <div className="flex flex-col min-h-screen bg-[var(--color-bg)] p-4 gap-6">
      <div className="sticky top-0 h-[35vh] bg-gradient-to-t ...">...</div>
      ...
    </div>
  );
}

// DOBRZE — screen jako kompozycja
export function SceneScreen() {
  return (
    <GameLayout>
      <SceneHeader />
      <NarrativeText text={node.text} onComplete={handleTextComplete} />
      <ChoicePanel choices={node.choices} onSelect={handleChoice} locked={choiceLocked} />
    </GameLayout>
  );
}
```

### 5. Folder `shared/` — komponenty wielokrotnego użytku

```
src/shared/
  Button/
    Button.tsx          # komponent z wariantami i rozmiarami przez propsy
    Button.types.ts     # typy propsów
    index.ts
  Container/            # gotowe wrappery layoutu (PageContainer, CardContainer itp.)
  Typography/           # Text, Heading, Paragraph ze zmiennymi stylami
  Animations/           # gotowe klasy animacji (hover efekty, fade-in itp.)
  tokens/
    colors.ts           # eksportowane stałe kolorów z CSS variables
    theme.ts            # definicje motywów dark/light/high-contrast
```

**Reguła `shared/`:** Zmiana komponentu w `shared/` wpływa na każde jego użycie w aplikacji.
Przed modyfikacją sprawdź wszystkie miejsca użycia (`grep -r "ComponentName" src/`).
Jeśli zmiana dotyczy tylko jednego miejsca — nie modyfikuj `shared/`, stwórz lokalny komponent.

### 6. Motywy: dark, light, high-contrast

Trzy motywy wstrzykiwane jako klasy na `<body>`: `theme-dark` (domyślny), `theme-light`, `theme-high-contrast`.
Wszystkie kolory przez CSS Variables — żaden kolor nie jest hardkodowany w komponencie.

```css
/* themes.css */
.theme-dark {
  --color-bg: #1a0a0a;
  --color-surface: #2a1010;
  --color-accent: #cc2200;
  --color-text: #f0e0d0;
  --color-border: #cc2200;
}
.theme-light {
  --color-bg: #f5f0eb;
  --color-surface: #ffffff;
  --color-accent: #cc2200;
  --color-text: #1a0a0a;
  --color-border: #cc2200;
}
.theme-high-contrast {
  --color-bg: #000000;
  --color-surface: #111111;
  --color-accent: #ff0000;
  --color-text: #ffffff;
  --color-border: #ffffff;
}
```

Przełącznik motywu musi być dostępny z każdego ekranu (w nagłówku lub stałym miejscu UI).

### 7. Folder dokumentacji technicznej `docs/`

```
frontend/docs/
  ARCHITECTURE.md       # diagram modułów, przepływ danych, stan gry
  COMPONENTS.md         # lista shared/ komponentów, ich propsy i użycia
  SCREENS.md            # każdy ekran: co renderuje, jakie komponenty, jaki stan czyta
  INTEGRATIONS.md       # API, service worker, PWA
  DECISIONS.md          # uzasadnienia wyborów technicznych (co i dlaczego)
```

**Reguła aktualizacji:** Każda zmiana w architekturze, nowy komponent w `shared/` lub nowy ekran
→ odpowiedni plik `docs/` aktualizowany w tej samej sesji pracy. Pliki `docs/` są plikami
kontekstowymi dla AI — muszą odzwierciedlać aktualny stan kodu, nie plany.

## Struktura plików

```
frontend/
  src/
    main.tsx                  # montowanie, rejestracja SW
    App.tsx                   # główny kontener, pobieranie danych, ThemeProvider
    shared/                   # komponenty wielokrotnego użytku (patrz zasada 5)
      Button/
      Container/
      Typography/
      Animations/
      tokens/
    game/
      types.ts                # typy: Story, Character, Decision, Choice, Ending, GameState
      reducer.ts              # gameReducer + initialState
      context.tsx             # GameContext + useGame hook
    screens/                  # tylko kompozycja komponentów (patrz zasada 4)
      LoadingScreen.tsx
      ErrorScreen.tsx
      StartScreen.tsx
      SceneScreen.tsx
      ConsequenceScreen.tsx
      EndingScreen.tsx
    components/               # komponenty specyficzne dla gry
      GameLayout.tsx
      SceneHeader.tsx
      NarrativeText.tsx       # karaoke word-by-word renderer
      ChoicePanel.tsx
      CharacterCard.tsx
      ConsequenceView.tsx
    styles/
      base.css                # @tailwind dyrektywy
      themes.css              # .theme-dark, .theme-light, .theme-high-contrast
  docs/                       # dokumentacja techniczna (patrz zasada 7)
    ARCHITECTURE.md
    COMPONENTS.md
    SCREENS.md
    INTEGRATIONS.md
    DECISIONS.md
  public/
    manifest.webmanifest
    icons/
    sw.js
  index.html
  vite.config.ts
```

## Ekrany i flow

```
[LoadingScreen] → fetch /api/story
    ↓ błąd
[ErrorScreen] → retry → [LoadingScreen]
    ↓ sukces
[StartScreen] → wybór postaci → entry_node_id postaci
    ↓
[SceneScreen] → kliknięcie opcji → wybrany Choice
    ↓
[ConsequenceScreen] → kliknięcie "Dalej" → next_node_id
    ↓
[SceneScreen] × 5 kolejnych decyzji (łącznie 6)
    ↓ ostatnia decyzja (węzeł type="ending")
[EndingScreen] → "Zagraj ponownie" → [StartScreen]
```

Wybór postaci **nie zwiększa** licznika decyzji. `ConsequenceScreen` pojawia się po każdej decyzji; "Dalej" nie jest decyzją.

## Stan gry (`GameState`)

```typescript
type Screen = 'loading' | 'error' | 'start' | 'scene' | 'consequence' | 'ending';

interface GameState {
  screen: Screen;
  story: Story | null;
  character: Character | null;
  currentNodeId: string | null;
  decisionCount: number;           // 0–6, rośnie przy wyborze opcji
  pendingChoice: Choice | null;    // wybrana opcja, czeka na "Dalej"
  choiceLocked: boolean;           // ochrona przed podwójnym kliknięciem
  errorMessage: string | null;
}
```

Akcje reducera: `STORY_LOADED`, `STORY_ERROR`, `SELECT_CHARACTER`, `SELECT_CHOICE`, `ADVANCE_SCENE`, `RESTART`, `RETRY_FETCH`.

Brak localStorage — odświeżenie resetuje grę. `StartScreen` wyświetla komunikat "Odświeżenie rozpoczyna grę od nowa".

## Art Direction — styl Helltaker

Komikso-kreskówkowy: grube kontury (2–3px solid), płaskie kolory, kanciaste narożniki, zero zaokrągleń i cieni.

**Paleta (zmienne CSS):**
```css
--color-bg: #1a0a0a;
--color-surface: #2a1010;
--color-accent: #cc2200;     /* krwista czerwień */
--color-text: #f0e0d0;
--color-border: #cc2200;
--color-border-hover: #ff4422;
```

**Przyciski opcji (`ChoiceButton`):**
- Border: `2px solid var(--color-border)`, narożniki z pseudo-elementami `::before/::after` tworzącymi kanciastą "ozdobę"
- `:hover`: kolor ramki → `--color-border-hover`, `translateY(-2px)`
- `:active`: `translateY(1px)`, jasny fill tła
- Tekst wyśrodkowany, zawijanie na wiele wierszy, min-height zapewniający czytelność

**Typografia:**
- Systemowe serif dla narracji (`Georgia, serif`), sans-serif dla UI
- Akapity: `line-height: 1.7`, `max-width: 65ch`
- Brak ilustracji i ozdobnych animacji (poza karaoke)

## Motywy

Klasy na `<body>`: `theme-day`, `theme-night` (domyślny), `theme-indoor`. Zmieniają zmienne CSS.
Przełącznik motywu to dodatkowy element UI, nieblokujący odbioru v0 — zaimplementuj tylko jeśli masz czas.

## Efekt Karaoke (`NarrativeText`)

Tekst narracji renderuje się słowo po słowie lub zdanie po zdaniu. Aktualnie "wchodzące" słowo jest pogrubione i w kolorze `--color-accent`.

- Implementacja: `useState` + `useEffect` z `setInterval` (ok. 60ms/słowo) lub requestAnimationFrame
- Kliknięcie w obszar tekstu lub `Space`/`Enter` → natychmiastowe pokazanie całego tekstu ("skip")
- Po zakończeniu karaoke przyciski opcji stają się aktywne (`choiceLocked` → `false`)
- Na `ConsequenceScreen` efekt karaoke jest opcjonalny (krótki tekst)

## Dostępność i klawiatura

- Klawisze `1`, `2` (ewentualnie `3`) → wybierają odpowiednią opcję (gdy widoczne)
- `Enter`/`Space` na `ConsequenceScreen` → Dalej
- Po zmianie ekranu: `focus()` na pierwszy nagłówek lub przycisk sceny
- Semantyczne elementy: `<main>`, `<section>`, `role="button"`, `aria-label` na przyciskach opcji
- Widoczny `:focus-visible` (nie chowaj outline)
- Komunikaty błędów i stanów w `aria-live="polite"`

## Układ responsywny

**Mobile (PWA — priorytet):**
```
┌─────────────────────┐
│  STICKY (35vh)      │ ← gradient od dołu (bg-gradient-to-t)
│  obrazek kontekst.  │    (placeholder div z kolorem tła, bez ilustracji w v0)
├─────────────────────┤
│  SCROLL             │ ← tekst narracji, akapity
│  ...                │
├─────────────────────┤
│  FIXED BOTTOM       │ ← panel decyzji, backdrop-blur
│  [Opcja 1] [Opcja 2]│
└─────────────────────┘
```

**Desktop (≥768px):**
```
┌───────────────┬──────────────────────┐
│  LEWA         │  PRAWA               │
│  tekst narracji│  obrazek/kolor      │
│  wyśrodkowany │  kontekstowy         │
│  pionowo      │                      │
├───────────────┴──────────────────────┤
│  panel decyzji (cały dół)            │
└──────────────────────────────────────┘
```

Minimum: `360px` bez poziomego scrollu. Duże przyciski (min-height 48px). Zawijanie długich opcji.

## Integracja API

```typescript
// App.tsx — jednorazowe pobranie
useEffect(() => {
  fetch('/api/story')
    .then(res => {
      if (!res.ok) throw new Error(`${res.status}`);
      return res.json();
    })
    .then(data => dispatch({ type: 'STORY_LOADED', payload: data }))
    .catch(err => dispatch({ type: 'STORY_ERROR', payload: err.message }));
}, []);
```

Po pobraniu gra działa wyłącznie lokalnie. Nie wysyłaj wyborów do serwera. Proxy `/api` skonfigurowane w `vite.config.ts` dla dev i preview.

## PWA (zakres frontendu)

- `manifest.webmanifest`: `name`, `short_name`, `start_url: "/"`, `display: "standalone"`, `theme_color`, lokalne ikony
- Service Worker (workbox lub ręczny): cache powłoki aplikacji (HTML, JS, CSS, ikony)
- **Nie cache'uj** `/api/story`
- Przy otwarciu bez sieci: powłoka ładuje się, gra próbuje fetch, `ErrorScreen` z informacją "Brak połączenia — odśwież po podłączeniu do sieci"
- Rejestracja SW tylko w produkcyjnym buildzie

## Kolejność implementacji (dla osoby D→A)

1. **D01** Vite + React + TS (scaffolding, Tailwind setup)
2. **D02** `types.ts` + neutralny fixture `content/legend.json`
3. **D03** `base.css` + `themes.css` + minimalne style mobilne
4. **D04** `vite.config.ts` proxy + `manifest.webmanifest` + `sw.js` skeleton
5. **A01** `reducer.ts` + `context.tsx` + stan gry
6. **A02** `StartScreen` (dwie karty postaci)
7. **A03** `SceneScreen` + `NarrativeText` (bez karaoke) + `ChoiceButton`
8. **A04** `ConsequenceScreen` + logika `choiceLocked`
9. **A05** `EndingScreen` + licznik + restart
10. **A06** `App.tsx` fetch + `LoadingScreen` + `ErrorScreen`
11. **A07** fokus, klawiatura, karaoke w `NarrativeText`

## Otwarte decyzje architektoniczne (do rozstrzygnięcia po v0)

### Kontekstowe stylowanie UI — epoka, pora dnia, miejsce

**Problem:** Każda legenda pochodzi z innej epoki historycznej. Chcemy, żeby elementy UI (szczególnie
ramki przycisków, typografia, ornamentyka) wizualnie nawiązywały do danego okresu. Na to nakłada się
dodatkowy kontekst: pora dnia i miejsce akcji.

**Dwie konkurujące opcje:**

**A) Szablony (templates) uzupełniane kontekstem**
Jeden komponent `Button` przyjmuje props `era` / `timeOfDay` / `location` i dynamicznie dobiera styl.
```tsx
<ChoiceButton era="medieval" timeOfDay="night" location="castle" />
```
- `+` mniej plików, jeden punkt zmiany
- `+` łatwo dodać nową kombinację przez konfigurację
- `-` trudno przewidzieć jak będzie wyglądał każdy wariant bez uruchomienia
- `-` ryzyko kombinatorycznej eksplozji (3 epoki × 3 pory × 4 miejsca = 36 wariantów)

**B) Gotowe warianty (preset components)**
Osobne komponenty lub klasy per epoka: `MedievalButton`, `BaroqueButton` itp.
```tsx
<MedievalButton variant="night" />
```
- `+` każdy wariant jest jawny, łatwy do przejrzenia i przetestowania wizualnie
- `+` designer/developer widzi dokładnie co wdraża
- `-` więcej plików, duplikacja bazowej logiki przycisku
- `-` trudniejsza globalna zmiana (np. rozmiar fontu we wszystkich epokach)

**Wstępna decyzja kierunkowa:** Warianty różnią się kształtem ramki (nie tylko kolorem)
→ skłania to ku opcji **B (presety)**. Dynamiczny template działałby dobrze dla samych kolorów,
ale różne kształty ramek to de facto osobne komponenty — lepiej nazwać je wprost niż ukrywać
za propsem `era="medieval"` który i tak renderuje inny SVG/CSS clip-path.

**Proponowana struktura przy opcji B:**
```
src/shared/Button/
  Button.tsx              # bazowa logika (onClick, disabled, size, children)
  variants/
    MedievalButton.tsx    # gotyckie kanciaste ramki
    BaroqueButton.tsx     # ozdobne, zaokrąglone ornamenty
    ModernButton.tsx      # minimalistyczny, flat
  index.ts                # eksportuje wszystkie warianty
```
Każdy wariant importuje bazowy `Button` i nakłada własną ramkę przez CSS/SVG.
Pora dnia i miejsce to oddzielna warstwa — tylko kolor/jasność, przez CSS Variables (patrz motywy).

**Pozostałe pytania do ustalenia:**
- Ile epok planujemy realnie obsłużyć? (3 legendy = potencjalnie 3 różne zestawy)
- Kto projektuje kształty ramek — developer w CSS czy designer w SVG/Figma?
- Czy ramki będą animowane (hover zmienia kształt) czy tylko kolor?

**Nie implementuj tego w v0.** Zanotuj finalną decyzję w `docs/DECISIONS.md` gdy zostanie podjęta.

---

## Czego nie robić

- Nie dodawaj React Router, Zustand, Framer Motion, Radix, Headless UI
- Nie hardkoduj ID postaci ani tekstów w komponentach
- Nie cache'uj stanu gry w localStorage
- Nie buduj ogólnego silnika RPG z warunkami i punktacją
- Nie dodawaj ilustracji, audio ani animacji poza karaoke
- Nie konteneryzuj frontendu (Docker tylko dla backend + baza)
