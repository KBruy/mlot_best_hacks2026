import type { Choice, Character, Story, GameState } from './types'

export type GameAction =
  | { type: 'STORY_LOADED'; payload: Story }
  | { type: 'STORY_ERROR'; payload: string }
  | { type: 'SELECT_CHARACTER'; payload: Character }
  | { type: 'SELECT_CHOICE'; payload: Choice }
  | { type: 'ADVANCE_SCENE' }
  | { type: 'RESTART' }
  | { type: 'RETRY_FETCH' }

export const initialState: GameState = {
  screen: 'loading',
  story: null,
  character: null,
  currentNodeId: null,
  decisionCount: 0,
  pendingChoice: null,
  choiceLocked: false,
  errorMessage: null,
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'STORY_LOADED':
      return { ...initialState, screen: 'start', story: action.payload }

    case 'STORY_ERROR':
      return { ...state, screen: 'error', errorMessage: action.payload }

    case 'SELECT_CHARACTER':
      return {
        ...state,
        screen: 'scene',
        character: action.payload,
        currentNodeId: action.payload.entry_node_id,
        decisionCount: 0,
        pendingChoice: null,
        choiceLocked: false,
      }

    case 'SELECT_CHOICE':
      if (state.choiceLocked) return state
      return {
        ...state,
        screen: 'consequence',
        pendingChoice: action.payload,
        choiceLocked: true,
        decisionCount: state.decisionCount + 1,
      }

    case 'ADVANCE_SCENE': {
      if (!state.pendingChoice) return state
      const nextId = state.pendingChoice.next_node_id
      const nextNode = state.story?.nodes.find(n => n.id === nextId)
      const nextScreen = nextNode?.type === 'ending' ? 'ending' : 'scene'
      return {
        ...state,
        screen: nextScreen,
        currentNodeId: nextId,
        pendingChoice: null,
        choiceLocked: false,
      }
    }

    case 'RESTART':
      return { ...initialState, screen: 'start', story: state.story }

    case 'RETRY_FETCH':
      return { ...initialState, screen: 'loading' }

    default:
      return state
  }
}
