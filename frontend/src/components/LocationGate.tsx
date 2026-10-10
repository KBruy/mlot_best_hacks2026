import { useEffect, useRef } from 'react'
import { PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { HintText } from './HintText'
import { useGame } from '../game/useGame'
import { bearingDeg } from '../map/distance'
import type { NodeLocation } from '../game/types'

interface Props {
  location: NodeLocation
  distanceM: number | null
}

function formatDistance(m: number): string {
  if (m < 1000) return `${Math.round(m)} m`
  return `${(m / 1000).toFixed(1)} km`
}

export function LocationGate({ location, distanceM }: Props) {
  const { state } = useGame()
  const { gpsPosition } = state

  const svRef0 = useRef<HTMLIFrameElement>(null)
  const svRef1 = useRef<HTMLIFrameElement>(null)
  const mapRef = useRef<HTMLIFrameElement>(null)
  const frontRef = useRef(0)
  const prevSvUrlRef = useRef('')

  const svLat = gpsPosition?.lat ?? location.streetview.lat
  const svLon = gpsPosition?.lon ?? location.streetview.lon
  const heading = gpsPosition
    ? bearingDeg(gpsPosition.lat, gpsPosition.lon, location.lat, location.lon)
    : location.streetview.heading

  const svUrl = `https://maps.google.com/maps?layer=c&cbll=${svLat},${svLon}&cbp=12,${heading},0,0,0&output=svembed`
  const mapUrl = `https://maps.google.com/maps?q=${svLat},${svLon}&z=17&t=k&output=embed`

  useEffect(() => {
    if (svUrl === prevSvUrlRef.current) return

    if (!prevSvUrlRef.current) {
      prevSvUrlRef.current = svUrl
      if (svRef0.current) svRef0.current.src = svUrl
      return
    }

    prevSvUrlRef.current = svUrl
    const backIdx = 1 - frontRef.current
    const back = backIdx === 0 ? svRef0.current : svRef1.current
    const front = frontRef.current === 0 ? svRef0.current : svRef1.current
    if (!back) return

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
    back.src = svUrl
  }, [svUrl])

  useEffect(() => {
    if (mapRef.current) mapRef.current.src = mapUrl
  }, [mapUrl])

  return (
    <PixelCard title={`Idź do: ${location.label}`}>
      <div className="relative h-52 rounded overflow-hidden mb-4">
        <iframe
          ref={svRef0}
          title={`Street View: ${location.label}`}
          allowFullScreen
          className="absolute inset-0 w-full h-full border-0"
          style={{ opacity: 1, transition: 'opacity 0.5s' }}
        />
        <iframe
          ref={svRef1}
          title={`Street View 2: ${location.label}`}
          allowFullScreen
          className="absolute inset-0 w-full h-full border-0"
          style={{ opacity: 0, pointerEvents: 'none', transition: 'opacity 0.5s' }}
        />
      </div>
      <iframe
        ref={mapRef}
        title={`Mapa: ${location.label}`}
        className="w-full h-32 rounded mb-4 border-0"
      />
      <NarrativeText className="mb-2">
        Aby odblokować tę scenę, musisz się tu udać.
      </NarrativeText>
      {distanceM !== null ? (
        <HintText>Jesteś w odległości {formatDistance(distanceM)} od celu</HintText>
      ) : (
        <HintText>Oczekiwanie na sygnał GPS…</HintText>
      )}
    </PixelCard>
  )
}
