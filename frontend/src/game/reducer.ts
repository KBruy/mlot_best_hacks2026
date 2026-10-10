import type { Choice, GpsPosition, Story, GameState } from './types'

export type GameAction =
  | { type: 'STORY_LOADED'; payload: Story }
  | { type: 'STORY_ERROR'; payload: string }
  | { type: 'SUMMARIES_LOADED' }
  | { type: 'START_STORY'; payload: Story }
  | { type: 'SELECT_CHOICE'; payload: Choice }
  | { type: 'ADVANCE_SCENE' }
  | { type: 'RESTART' }
  | { type: 'RETRY_FETCH' }
  | { type: 'GPS_UPDATE'; payload: GpsPosition }
  | { type: 'TOGGLE_DEMO_MODE' }

export const initialState: GameState = {
  screen: 'loading',
  story: null,
  currentNodeId: null,
  decisionCount: 0,
  pendingChoice: null,
  choiceLocked: false,
  errorMessage: null,
  gpsPosition: null,
  demoMode: false,
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'STORY_LOADED':
      return { ...initialState, screen: 'start', story: action.payload, demoMode: state.demoMode }

    case 'STORY_ERROR':
      return { ...state, screen: 'error', errorMessage: action.payload }

    case 'SUMMARIES_LOADED':
      return { ...state, screen: 'start' }

    case 'START_STORY':
      return {
        ...initialState,
        screen: 'scene',
        story: action.payload,
        currentNodeId: action.payload.entry_node_id,
        demoMode: state.demoMode,
        gpsPosition: state.gpsPosition,
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
      return {
        ...state,
        screen: nextNode?.type === 'ending' ? 'ending' : 'scene',
        currentNodeId: nextId,
        pendingChoice: null,
        choiceLocked: false,
      }
    }

    case 'RESTART':
      return {
        ...initialState,
        screen: 'start',
        story: state.story,
        demoMode: state.demoMode,
        gpsPosition: state.gpsPosition,
      }

    case 'RETRY_FETCH':
      return { ...initialState, demoMode: state.demoMode }

    case 'GPS_UPDATE':
      return { ...state, gpsPosition: action.payload }

    case 'TOGGLE_DEMO_MODE':
      return { ...state, demoMode: !state.demoMode }

    default:
      return state
  }
}
