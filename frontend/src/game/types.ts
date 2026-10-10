export interface Choice {
  id: string
  text: string
  consequence: string
  next_node_id: string
}

export interface NodeLocation {
  lat: number
  lon: number
  radius_m: number
  label: string
  streetview: {
    lat: number
    lon: number
    heading: number
    pitch: number
  }
}

export interface DecisionNode {
  id: string
  type: 'decision'
  text: string
  choices: Choice[]
  location?: NodeLocation
}

export interface EndingNode {
  id: string
  type: 'ending'
  title: string
  text: string
}

export type StoryNode = DecisionNode | EndingNode

export interface Character {
  id: string
  name: string
  description: string
  entry_node_id: string
}

export interface Story {
  id: string
  title: string
  intro: string
  entry_node_id: string
  characters: Character[]
  nodes: StoryNode[]
}

export type Screen = 'loading' | 'error' | 'start' | 'scene' | 'consequence' | 'ending'

export interface GpsPosition {
  lat: number
  lon: number
}

export interface GameState {
  screen: Screen
  story: Story | null
  currentNodeId: string | null
  decisionCount: number
  pendingChoice: Choice | null
  choiceLocked: boolean
  errorMessage: string | null
  gpsPosition: GpsPosition | null
  demoMode: boolean
}
