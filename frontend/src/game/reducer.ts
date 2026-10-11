import type { Option, Story, GameState, GpsPosition } from './types'
import { haversineDistance } from '../map/distance'

export type GameAction =
  | { type: 'SUMMARIES_LOADED' }
  | { type: 'STORY_ERROR'; payload: string }
  | { type: 'START_STORY'; payload: Story }
  | { type: 'SELECT_OPTION'; payload: Option }
  | { type: 'ADVANCE_SCENE' }
  | { type: 'RESTART' }
  | { type: 'RETRY_FETCH' }
  | { type: 'GPS_UPDATE'; payload: GpsPosition }
  | { type: 'TOGGLE_DEMO_MODE' }

export const initialState: GameState = {
  screen: 'loading',
  story: null,
  currentSceneId: null,
  gameFields: {},
  decisionCount: 0,
  pendingOption: null,
  choiceLocked: false,
  errorMessage: null,
  gpsPosition: null,
  demoMode: false,
}

function resolveWidok(lat: number, lon: number, story: Story): string {
  const vp = story.location.viewpoints.find(
    v => haversineDistance(lat, lon, v.lat, v.lon) <= v.radius_m,
  )
  return vp?.id ?? story.location.default_view
}

export function gameReducer(state: GameState, action: GameAction): GameState {
  switch (action.type) {
    case 'SUMMARIES_LOADED':
      return { ...state, screen: 'start' }

    case 'STORY_ERROR':
      return { ...state, screen: 'error', errorMessage: action.payload }

    case 'START_STORY': {
      const story = action.payload
      const widok = state.gpsPosition
        ? resolveWidok(state.gpsPosition.lat, state.gpsPosition.lon, story)
        : story.location.default_view
      return {
        ...initialState,
        screen: 'scene',
        story,
        currentSceneId: story.start,
        gameFields: { widok },
        demoMode: state.demoMode,
        gpsPosition: state.gpsPosition,
      }
    }

    case 'SELECT_OPTION':
      if (state.choiceLocked) return state
      return {
        ...state,
        screen: 'consequence',
        pendingOption: action.payload,
        gameFields: { ...state.gameFields, ...action.payload.set },
        choiceLocked: true,
        decisionCount: state.decisionCount + 1,
      }

    case 'ADVANCE_SCENE': {
      if (!state.pendingOption || !state.story) return state
      const nextId = state.pendingOption.next
      if (nextId === null) {
        const endingKey = state.story.ending_by
          .map(field => state.gameFields[field] ?? '')
          .join('|')
        return {
          ...state,
          screen: 'ending',
          currentSceneId: endingKey,
          pendingOption: null,
          choiceLocked: false,
        }
      }
      return {
        ...state,
        screen: 'scene',
        currentSceneId: nextId,
        pendingOption: null,
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

    case 'GPS_UPDATE': {
      const newFields = { ...state.gameFields }
      if (state.story) {
        newFields.widok = resolveWidok(action.payload.lat, action.payload.lon, state.story)
      }
      return { ...state, gpsPosition: action.payload, gameFields: newFields }
    }

    case 'TOGGLE_DEMO_MODE':
      return { ...state, demoMode: !state.demoMode }

    default:
      return state
  }
}
