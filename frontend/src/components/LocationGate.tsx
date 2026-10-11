import { useEffect, useRef, useMemo, useState } from 'react'
import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { NavMap } from './NavMap'
import { useGame } from '../game/useGame'
import { haversineDistance, bearingDeg } from '../map/distance'
import type { Stop, StreetViewShot } from '../game/types'

interface Props {
  stop: Stop
  shot?: StreetViewShot | null
  anchors?: [number, number][] | null
  skippable?: boolean
  distanceM: number | null
  onSkip?: () => void
}

const ANCHOR_RANGE_M = 35
const SLIDE_INTERVAL_MS = 3000

function formatDistance(m: number): string {
  if (m < 1000) return `${Math.round(m)} m`
  return `${(m / 1000).toFixed(1)} km`
}

function svUrl(lat: number, lon: number, heading: number, pitch: number): string {
  return `https://maps.google.com/maps?layer=c&cbll=${lat},${lon}&cbp=12,${heading},0,0,${pitch}&output=svembed`
}

export function LocationGate({ stop, shot, anchors, skippable, distanceM, onSkip }: Props) {
  const { state, dispatch } = useGame()
  const gps = state.gpsPosition

  // Demo: cycle through anchors as slideshow
  const [slideIndex, setSlideIndex] = useState(0)

  useEffect(() => {
    if (!skippable || !anchors?.length) return
    const id = setInterval(() => {
      setSlideIndex(i => (i + 1) % anchors.length)
    }, SLIDE_INTERVAL_MS)
    return () => clearInterval(id)
  }, [skippable, anchors])

  const activeView = useMemo(() => {
    if (skippable && anchors?.length) {
      const [ancLat, ancLon] = anchors[slideIndex]
      return {
        lat: ancLat,
        lon: ancLon,
        heading: bearingDeg(ancLat, ancLon, stop.lat, stop.lon),
        pitch: 0,
      }
    }

    if (!gps || !anchors?.length) return shot ?? null

    let nearestDist = Infinity
    let nearestAnchor = anchors[0]
    for (const a of anchors) {
      const d = haversineDistance(gps.lat, gps.lon, a[0], a[1])
      if (d < nearestDist) { nearestDist = d; nearestAnchor = a }
    }

    if (nearestDist > ANCHOR_RANGE_M) return shot ?? null

    const [ancLat, ancLon] = nearestAnchor
    return {
      lat: ancLat,
      lon: ancLon,
      heading: bearingDeg(ancLat, ancLon, stop.lat, stop.lon),
      pitch: 0,
    }
  }, [gps, anchors, stop, shot, skippable, slideIndex])

  const currentUrl = activeView
    ? svUrl(activeView.lat, activeView.lon, activeView.heading, activeView.pitch)
    : null

  const svRef0 = useRef<HTMLIFrameElement>(null)
  const svRef1 = useRef<HTMLIFrameElement>(null)
  const frontRef = useRef(0)
  const shownUrlRef = useRef('')

  useEffect(() => {
    if (!currentUrl || currentUrl === shownUrlRef.current) return

    const backIdx = 1 - frontRef.current
    const back = backIdx === 0 ? svRef0.current : svRef1.current
    const front = frontRef.current === 0 ? svRef0.current : svRef1.current

    if (!back) return

    if (!shownUrlRef.current) {
      back.src = currentUrl
      back.style.opacity = '1'
      back.style.pointerEvents = 'auto'
      frontRef.current = backIdx
      shownUrlRef.current = currentUrl
      return
    }

    shownUrlRef.current = currentUrl

    const handleLoad = () => {
      back.style.opacity = '1'
      back.style.pointerEvents = 'auto'
      if (front) {
        front.style.opacity = '0'
        front.style.pointerEvents = 'none'
      }
      frontRef.current = backIdx
      back.removeEventListener('load', handleLoad)
    }
    back.addEventListener('load', handleLoad)
    back.src = currentUrl
  }, [currentUrl])

  return (
    <PixelCard title={`Idź do: ${stop.label}`}>
      {currentUrl && (
        <div className="relative h-52 overflow-hidden mb-3">
          <iframe
            ref={svRef0}
            title={`Street View: ${stop.label}`}
            allowFullScreen
            className="absolute inset-0 w-full h-full border-0"
            style={{ opacity: 0, transition: 'opacity 0.5s' }}
          />
          <iframe
            ref={svRef1}
            title={`Street View 2: ${stop.label}`}
            allowFullScreen
            className="absolute inset-0 w-full h-full border-0"
            style={{ opacity: 0, pointerEvents: 'none', transition: 'opacity 0.5s' }}
          />
        </div>
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
      <NarrativeText className="mb-3">{stop.walk}</NarrativeText>
      {skippable ? (
        <PixelButton tone="gold" className="w-full" onClick={onSkip}>
          Dalej
        </PixelButton>
      ) : (
        <PixelButton
          tone="gold"
          className="w-full"
          disabled={distanceM === null || distanceM > stop.radius_m}
          onClick={() => dispatch({ type: 'MANUAL_ARRIVE' })}
        >
          {distanceM === null
            ? 'Oczekiwanie na GPS…'
            : distanceM > stop.radius_m
              ? `Dojdź bliżej (${formatDistance(distanceM)})`
              : 'Wejdź →'}
        </PixelButton>
      )}
    </PixelCard>
  )
}
