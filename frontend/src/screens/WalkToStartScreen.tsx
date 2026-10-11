import { useMemo } from 'react'
import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { haversineDistance, bearingDeg } from '../map/distance'
import { NavMap } from '../components/NavMap'
import { StreetViewEmbed } from '../components/StreetViewEmbed'
import type { Story, StreetViewShot } from '../game/types'

function nearestAnchorIdx(anchors: [number, number][], lat: number, lon: number): number {
  let best = 0
  let bestDist = Infinity
  for (let i = 0; i < anchors.length; i++) {
    const d = haversineDistance(lat, lon, anchors[i][0], anchors[i][1])
    if (d < bestDist) { bestDist = d; best = i }
  }
  return best
}

function destinationShot(story: Story): StreetViewShot | null {
  const anchors = story.streetview?.anchors
  if (!anchors?.length) return null
  const [clat, clon] = story.location.center
  const idx = nearestAnchorIdx(anchors, clat, clon)
  const [ancLat, ancLon] = anchors[idx]
  return { lat: ancLat, lon: ancLon, heading: bearingDeg(ancLat, ancLon, clat, clon), pitch: 0 }
}

function formatDistance(m: number): string {
  if (m < 1000) return `${Math.round(m)} m`
  return `${(m / 1000).toFixed(1)} km`
}

export function WalkToStartScreen() {
  const { state, dispatch } = useGame()
  const story = state.story!
  const { gpsGranted, gpsPosition } = state

  const shot = useMemo(() => destinationShot(story), [story])

  const distanceM = gpsPosition
    ? Math.round(haversineDistance(
        gpsPosition.lat, gpsPosition.lon,
        story.location.center[0], story.location.center[1],
      ))
    : null

  const inRange = distanceM !== null && distanceM <= story.location.unlock_radius_m
  const canBegin = gpsGranted === true && inRange

  const gpsDotClass = gpsGranted === true
    ? 'bg-green-500'
    : gpsGranted === false
      ? 'bg-red-500'
      : 'bg-retro-muted animate-pulse'

  const gpsLabel = gpsGranted === true
    ? 'GPS: aktywny'
    : gpsGranted === false
      ? 'GPS: brak dostępu'
      : 'GPS: oczekiwanie…'

  return (
    <main className="min-h-screen flex flex-col items-center justify-start gap-4 p-4 pt-8 bg-retro-bg overflow-y-auto">
      <div className="w-full max-w-md flex flex-col gap-4">

        <PixelCard title={`Dojdź do: ${story.location.name}`}>

          {/* Street View */}
          {shot && (
            <div className="relative h-52 overflow-hidden mb-3">
              <StreetViewEmbed point={shot} title={story.location.name} className="h-full" />
            </div>
          )}

          {/* NavMap */}
          <div className="h-40 mb-3 overflow-hidden border border-retro-border">
            <NavMap
              stopLat={story.location.center[0]}
              stopLon={story.location.center[1]}
              stopLabel={story.location.name}
              userLat={gpsPosition?.lat}
              userLon={gpsPosition?.lon}
            />
          </div>

          {/* GPS status + distance */}
          <div className="flex items-center justify-between gap-2 mb-3">
            <div className="flex items-center gap-1.5">
              <span className={['w-2.5 h-2.5 rounded-full shrink-0', gpsDotClass].join(' ')} />
              <span className={[
                'font-mono text-xs',
                gpsGranted === false ? 'text-red-400' : 'text-retro-muted',
              ].join(' ')}>
                {gpsLabel}
              </span>
            </div>
            {gpsGranted === true && distanceM !== null && (
              <span className={[
                'font-mono text-sm font-bold',
                inRange ? 'text-green-400' : 'text-retro-secondary',
              ].join(' ')}>
                {inRange ? '✓ Na miejscu' : formatDistance(distanceM)}
              </span>
            )}
          </div>

          {gpsGranted === false && (
            <p className="font-mono text-retro-muted text-xs leading-relaxed mb-3">
              Sprawdź ustawienia lokalizacji w telefonie i odśwież stronę.
            </p>
          )}

          {/* Begin button */}
          <PixelButton
            tone="gold"
            className="w-full"
            disabled={!canBegin}
            onClick={() => dispatch({ type: 'BEGIN_GAME' })}
          >
            {canBegin
              ? 'Wejdź do legendy →'
              : gpsGranted !== true
                ? 'Oczekiwanie na GPS…'
                : `Dojdź bliżej (${distanceM !== null ? formatDistance(distanceM) : '…'})`}
          </PixelButton>

        </PixelCard>

        {/* Demo card */}
        <PixelCard title="Tryb demo">
          <p className="font-mono text-retro-muted text-xs leading-relaxed mb-3">
            Zagraj z dowolnego miejsca — widoki Street View i mapa działają,
            spacer jest symulowany automatycznie.
          </p>
          <PixelButton
            tone="neutral"
            className="w-full"
            onClick={() => dispatch({ type: 'BEGIN_DEMO' })}
          >
            Zagraj w trybie demo
          </PixelButton>
        </PixelCard>

      </div>
    </main>
  )
}
