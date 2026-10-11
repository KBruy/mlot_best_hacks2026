import { useEffect, useRef } from 'react'
import L from 'leaflet'

interface Props {
  stopLat: number
  stopLon: number
  stopLabel: string
  userLat?: number | null
  userLon?: number | null
}

function destinationIcon() {
  return L.divIcon({
    className: '',
    html: `<div class="map-pin map-pin--selected"></div>`,
    iconSize: [18, 18],
    iconAnchor: [9, 9],
  })
}

function userIcon() {
  return L.divIcon({
    className: '',
    html: `<div style="width:12px;height:12px;border-radius:50%;background:#3b82f6;border:2px solid #fff;box-shadow:0 0 0 3px rgba(59,130,246,.4)"></div>`,
    iconSize: [12, 12],
    iconAnchor: [6, 6],
  })
}

export function NavMap({ stopLat, stopLon, stopLabel, userLat, userLon }: Props) {
  const containerRef = useRef<HTMLDivElement>(null)
  const mapRef = useRef<L.Map | null>(null)
  const destMarkerRef = useRef<L.Marker | null>(null)
  const userMarkerRef = useRef<L.Marker | null>(null)

  useEffect(() => {
    if (!containerRef.current || mapRef.current) return

    const map = L.map(containerRef.current, {
      center: [stopLat, stopLon],
      zoom: 17,
      zoomControl: false,
      attributionControl: false,
    })

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
    }).addTo(map)

    destMarkerRef.current = L.marker([stopLat, stopLon], { icon: destinationIcon() })
      .addTo(map)
      .bindTooltip(stopLabel, { direction: 'top', offset: [0, -4], permanent: true })

    mapRef.current = map

    return () => {
      map.remove()
      mapRef.current = null
      destMarkerRef.current = null
      userMarkerRef.current = null
    }
  }, [stopLat, stopLon, stopLabel])

  useEffect(() => {
    const map = mapRef.current
    if (!map || userLat == null || userLon == null) return

    if (userMarkerRef.current) {
      userMarkerRef.current.setLatLng([userLat, userLon])
    } else {
      userMarkerRef.current = L.marker([userLat, userLon], { icon: userIcon() }).addTo(map)
    }

    const bounds = L.latLngBounds([[stopLat, stopLon], [userLat, userLon]])
    map.fitBounds(bounds, { padding: [32, 32], maxZoom: 18, animate: true })
  }, [userLat, userLon, stopLat, stopLon])

  return <div ref={containerRef} className="h-full w-full" />
}
