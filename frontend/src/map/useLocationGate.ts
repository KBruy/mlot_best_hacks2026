import { useGame } from '../game/useGame'
import { haversineDistance } from './distance'
import type { DecisionNode } from '../game/types'

interface LocationGateResult {
  blocked: boolean
  distanceM: number | null
}

export function useLocationGate(node: DecisionNode): LocationGateResult {
  const { state } = useGame()

  if (state.demoMode || !node.location) {
    return { blocked: false, distanceM: null }
  }

  if (!state.gpsPosition) {
    return { blocked: true, distanceM: null }
  }

  const distanceM = haversineDistance(
    state.gpsPosition.lat,
    state.gpsPosition.lon,
    node.location.lat,
    node.location.lon,
  )

  return {
    blocked: distanceM > node.location.radius_m,
    distanceM: Math.round(distanceM),
  }
}
