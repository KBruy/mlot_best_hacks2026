import { useEffect, useRef } from 'react'
import L from 'leaflet'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  selectedId: string | null
  focusKey: number
  onSelect: (id: string) => void
}

const WROCLAW_CENTER: L.LatLngExpression = [51.1097, 17.0326]
const DEFAULT_ZOOM = 15

function createPinIcon(selected: boolean) {
  return L.divIcon({
    className: '',
    html: `<div class="map-pin${selected ? ' map-pin--selected' : ''}"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
    tooltipAnchor: [0, -11],
  })
}

export function LegendMap({ summaries, selectedId, focusKey, onSelect }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const markersRef = useRef<Map<string, L.Marker>>(new Map())
  const onSelectRef = useRef(onSelect)

  useEffect(() => {
    onSelectRef.current = onSelect
  }, [onSelect])

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = L.map(containerRef.current, {
      center: WROCLAW_CENTER,
      zoom: DEFAULT_ZOOM,
      zoomControl: true,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      maxZoom: 19,
    }).addTo(map)

    mapRef.current = map
    const markers = markersRef.current

    return () => {
      map.remove()
      mapRef.current = null
      markers.clear()
    }
  }, [])

  // Sync pins when summaries list changes
  useEffect(() => {
    const map = mapRef.current
    if (!map) return

    const incoming = new Set(summaries.map(s => s.id))

    markersRef.current.forEach((marker, id) => {
      if (!incoming.has(id)) {
        marker.remove()
        markersRef.current.delete(id)
      }
    })

    summaries.forEach(s => {
      if (markersRef.current.has(s.id)) return
      const marker = L.marker(s.location.center, { icon: createPinIcon(false) })
        .addTo(map)
        .bindTooltip(s.title, { direction: 'top', offset: [0, -4] })
        .on('click', () => onSelectRef.current(s.id))
      markersRef.current.set(s.id, marker)
    })
  }, [summaries])

  // Update selected pin style + pan
  useEffect(() => {
    markersRef.current.forEach((marker, id) => {
      marker.setIcon(createPinIcon(id === selectedId))
    })

    const map = mapRef.current
    if (!map || !selectedId) return
    const summary = summaries.find(s => s.id === selectedId)
    if (summary) {
      const targetZoom = DEFAULT_ZOOM + 1
      map.flyTo(summary.location.center, targetZoom, { animate: true, duration: 0.6 })
    }
  }, [selectedId, summaries, focusKey])

  return <div ref={containerRef} className="h-full w-full" />
}
