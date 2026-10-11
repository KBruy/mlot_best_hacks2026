import { PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { HintText } from './HintText'
import { NavMap } from './NavMap'
import { StreetViewEmbed } from './StreetViewEmbed'
import { useGame } from '../game/useGame'
import type { Stop, StreetViewShot } from '../game/types'

interface Props {
  stop: Stop
  shot?: StreetViewShot | null
  distanceM: number | null
}

function formatDistance(m: number): string {
  if (m < 1000) return `${Math.round(m)} m`
  return `${(m / 1000).toFixed(1)} km`
}

export function LocationGate({ stop, shot, distanceM }: Props) {
  const { state } = useGame()
  const gps = state.gpsPosition

  return (
    <PixelCard title={`Idź do: ${stop.label}`}>
      {shot && (
        <StreetViewEmbed
          point={shot}
          title={stop.label}
          className="h-52 mb-3"
        />
      )}
      <div className="h-36 mb-3 overflow-hidden border border-retro-border">
        <NavMap
          stopLat={stop.lat}
          stopLon={stop.lon}
          stopLabel={stop.label}
          userLat={gps?.lat}
          userLon={gps?.lon}
        />
      </div>
      <NarrativeText className="mb-2">{stop.walk}</NarrativeText>
      {distanceM !== null ? (
        <HintText>Jesteś w odległości {formatDistance(distanceM)} od celu</HintText>
      ) : (
        <HintText>Oczekiwanie na sygnał GPS…</HintText>
      )}
    </PixelCard>
  )
}
