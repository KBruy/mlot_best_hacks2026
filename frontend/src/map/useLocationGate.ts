import { useGame } from '../game/useGame'
import { haversineDistance } from './distance'
import type { Scene } from '../game/types'

interface LocationGateResult {
  blocked: boolean
  distanceM: number | null
}

export function useLocationGate(scene: Scene | null): LocationGateResult {
  const { state } = useGame()

  if (state.demoMode || !scene?.before) {
    return { blocked: false, distanceM: null }
  }

  const stop = state.story?.stops[scene.before]
  if (!stop) return { blocked: false, distanceM: null }

  if (!state.gpsPosition) {
    return { blocked: true, distanceM: null }
  }

  const distanceM = haversineDistance(
    state.gpsPosition.lat,
    state.gpsPosition.lon,
    stop.lat,
    stop.lon,
  )

  return {
    blocked: distanceM > stop.radius_m,
    distanceM: Math.round(distanceM),
  }
}
