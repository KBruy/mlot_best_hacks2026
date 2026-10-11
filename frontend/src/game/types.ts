// ── Text resolution system ────────────────────────────────────────────────────

export type Condition = Record<string, string[]>

export interface Variant {
  if?: Condition
  text: string
  audio_url?: string | null
}

export type Text = string | Variant | Variant[]
export type Paragraphs = Text[]

// ── Location ──────────────────────────────────────────────────────────────────

export interface Viewpoint {
  id: string
  label: string
  lat: number
  lon: number
  radius_m: number
}

export interface Location {
  name: string
  center: [number, number]
  unlock_radius_m: number
  default_view: string
  viewpoints: Viewpoint[]
}

// ── Stop & Route ──────────────────────────────────────────────────────────────

export interface Stop {
  label: string
  lat: number
  lon: number
  radius_m: number
  walk: string
  arrive: string
}

export interface Route {
  start: [number, number]
  legs: Record<string, [number, number][]>
}

// ── Street View ───────────────────────────────────────────────────────────────

export interface StreetViewShot {
  lat: number
  lon: number
  heading: number
  pitch: number
  note?: string | null
}

export interface StreetView {
  anchors: [number, number][]
  stops: Record<string, StreetViewShot>
  finale: StreetViewShot
}

// ── Scene & Option ────────────────────────────────────────────────────────────

export interface Option {
  text: Text
  legend: boolean
  set: Record<string, string>
  next: string | null
  result: Paragraphs
}

export interface Scene {
  title: string
  scene: Paragraphs
  options: Option[]
  fact: string
  act?: string | null
  before?: string | null
  keypoint?: string | null
  art?: string[] | null
}

// ── Endings & Finale ──────────────────────────────────────────────────────────

export interface Ending {
  title: string
  paragraphs: Paragraphs
}

export interface Finale {
  act?: string | null
  paragraphs: Paragraphs
}

export interface Reveal {
  title: string
  paragraphs: Paragraphs
}

export interface Rank {
  min: number
  title: string
  text: string
}

// ── Story ─────────────────────────────────────────────────────────────────────

export interface Story {
  id: string
  title: string
  location: Location
  stops: Record<string, Stop>
  route?: Route | null
  streetview?: StreetView | null
  demo_start?: [number, number] | null
  state: Record<string, string[]>
  intro: { title: string; paragraphs: Paragraphs }
  start: string
  scenes: Record<string, Scene>
  ending_by: string[]
  endings: Record<string, Ending>
  finale: Finale
  reveal: Reveal
  ranks: Rank[]
  heritage: Text
  look_up: Text
}

// ── StorySummary (GET /api/stories) ───────────────────────────────────────────

export interface StorySummaryLocation {
  name: string
  center: [number, number]
}

export interface StorySummary {
  id: string
  title: string
  location: StorySummaryLocation
  intro: { title: string; paragraphs: Paragraphs }
}

// ── Game state ────────────────────────────────────────────────────────────────


export type Screen = 'loading' | 'error' | 'start' | 'scene' | 'consequence' | 'ending'

export interface GpsPosition {
  lat: number
  lon: number
}

export type GameFields = Record<string, string>

export interface GameState {
  screen: Screen
  story: Story | null
  currentSceneId: string | null
  gameFields: GameFields
  decisionCount: number
  pendingOption: Option | null
  choiceLocked: boolean
  errorMessage: string | null
  gpsPosition: GpsPosition | null
  gpsGranted: boolean | null
  demoMode: boolean
  muted: boolean
}
