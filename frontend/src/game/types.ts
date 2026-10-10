export interface Choice {
  id: string
  text: string
  consequence: string
  next_node_id: string
}

export interface DecisionNode {
  id: string
  type: 'decision'
  text: string
  choices: Choice[]
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

export interface GameState {
  screen: Screen
  story: Story | null
  currentNodeId: string | null
  decisionCount: number
  pendingChoice: Choice | null
  choiceLocked: boolean
  errorMessage: string | null
}
