import type { Option, Story, GameState, GpsPosition } from './types'
import { haversineDistance } from '../map/distance'

export type GameAction =
  | { type: 'SUMMARIES_LOADED' }
  | { type: 'STORY_ERROR'; payload: string }
  | { type: 'START_STORY'; payload: Story }
  | { type: 'BEGIN_GAME' }
  | { type: 'BEGIN_DEMO' }
  | { type: 'SELECT_OPTION'; payload: Option }
  | { type: 'ADVANCE_SCENE' }
  | { type: 'DISMISS_ARRIVAL' }
  | { type: 'RESTART' }
  | { type: 'RETRY_FETCH' }
  | { type: 'GPS_UPDATE'; payload: GpsPosition }
  | { type: 'GPS_DENIED' }
  | { type: 'TOGGLE_DEMO_MODE' }
  | { type: 'TOGGLE_MUTE' }

export const initialState: GameState = {
  screen: 'loading',
  story: null,
  currentSceneId: null,
  gameFields: {},
  decisionCount: 0,
  legendScore: 0,
  pendingOption: null,
  choiceLocked: false,
  errorMessage: null,
  gpsPosition: null,
  gpsGranted: null,
  demoMode: false,
  muted: false,
  lastStop: null,
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
      if (state.demoMode) {
        const pos = story.demo_start
          ? { lat: story.demo_start[0], lon: story.demo_start[1] }
          : state.gpsPosition
        const widok = pos ? resolveWidok(pos.lat, pos.lon, story) : story.location.default_view
        return {
          ...initialState,
          screen: 'scene',
          story,
          currentSceneId: story.start,
          gameFields: { widok },
          demoMode: true,
          muted: state.muted,
          gpsPosition: state.gpsPosition,
          gpsGranted: state.gpsGranted,
        }
      }
      const widok = state.gpsPosition
        ? resolveWidok(state.gpsPosition.lat, state.gpsPosition.lon, story)
        : story.location.default_view
      return {
        ...initialState,
        screen: 'walk_to_start',
        story,
        currentSceneId: null,
        gameFields: { widok },
        demoMode: false,
        muted: state.muted,
        gpsPosition: state.gpsPosition,
        gpsGranted: state.gpsGranted,
      }
    }

    case 'BEGIN_GAME': {
      if (!state.story) return state
      const widok = state.gpsPosition
        ? resolveWidok(state.gpsPosition.lat, state.gpsPosition.lon, state.story)
        : state.story.location.default_view
      return {
        ...state,
        screen: 'scene',
        currentSceneId: state.story.start,
        gameFields: { ...state.gameFields, widok },
      }
    }

    case 'BEGIN_DEMO': {
      if (!state.story) return state
      const story = state.story
      const pos = story.demo_start
        ? { lat: story.demo_start[0], lon: story.demo_start[1] }
        : state.gpsPosition
      const widok = pos ? resolveWidok(pos.lat, pos.lon, story) : story.location.default_view
      return {
        ...state,
        screen: 'scene',
        currentSceneId: story.start,
        demoMode: true,
        gameFields: { ...state.gameFields, widok },
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
        legendScore: state.legendScore + (action.payload.legend ? 1 : 0),
      }

    case 'ADVANCE_SCENE': {
      if (!state.pendingOption || !state.story) return state
      const currentScene = state.currentSceneId ? state.story.scenes[state.currentSceneId] : null
      const lastStop = currentScene?.before ?? state.lastStop
      const nextId = state.pendingOption.next
      if (nextId === null) {
        const endingKey = state.story.ending_by
          .map(field => state.gameFields[field] ?? '')
          .join('|')
        return {
          ...state,
          lastStop,
          screen: 'ending',
          currentSceneId: endingKey,
          pendingOption: null,
          choiceLocked: false,
        }
      }
      return {
        ...state,
        lastStop,
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
        muted: state.muted,
        gpsPosition: state.gpsPosition,
        gpsGranted: state.gpsGranted,
      }

    case 'RETRY_FETCH':
      return { ...initialState, demoMode: state.demoMode, muted: state.muted, gpsGranted: state.gpsGranted }

    case 'GPS_UPDATE': {
      const newFields = { ...state.gameFields }
      if (state.story) {
        newFields.widok = resolveWidok(action.payload.lat, action.payload.lon, state.story)
      }

      let newScreen = state.screen
      if (state.screen === 'scene' && state.currentSceneId && state.story && !state.demoMode) {
        const scene = state.story.scenes[state.currentSceneId]
        const stop = scene?.before ? state.story.stops[scene.before] : null
        if (stop) {
          const prevDist = state.gpsPosition
            ? haversineDistance(state.gpsPosition.lat, state.gpsPosition.lon, stop.lat, stop.lon)
            : Infinity
          const nextDist = haversineDistance(action.payload.lat, action.payload.lon, stop.lat, stop.lon)
          if (prevDist > stop.radius_m && nextDist <= stop.radius_m) {
            newScreen = 'arrive'
          }
        }
      }

      return { ...state, screen: newScreen, gpsPosition: action.payload, gpsGranted: true, gameFields: newFields }
    }

    case 'DISMISS_ARRIVAL':
      return { ...state, screen: 'scene' }

    case 'GPS_DENIED':
      return { ...state, gpsGranted: false }

    case 'TOGGLE_DEMO_MODE':
      return { ...state, demoMode: !state.demoMode }

    case 'TOGGLE_MUTE':
      return { ...state, muted: !state.muted }

    default:
      return state
  }
}
