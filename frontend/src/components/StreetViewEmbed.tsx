import { useEffect, useRef } from 'react'

interface StreetViewPoint {
  lat: number
  lon: number
  heading: number
  pitch: number
}

interface Props {
  point: StreetViewPoint
  title: string
  className?: string
}

function svUrl({ lat, lon, heading, pitch }: StreetViewPoint): string {
  return (
    `https://maps.google.com/maps?layer=c` +
    `&cbll=${lat},${lon}` +
    `&cbp=12,${heading},0,0,${pitch}` +
    `&output=svembed`
  )
}

export function StreetViewEmbed({ point, title, className = '' }: Props) {
  const svRef0 = useRef<HTMLIFrameElement>(null)
  const svRef1 = useRef<HTMLIFrameElement>(null)
  const frontRef = useRef(0)
  const shownUrlRef = useRef('')

  const url = svUrl(point)

  useEffect(() => {
    if (url === shownUrlRef.current) return

    const backIdx = 1 - frontRef.current
    const back = backIdx === 0 ? svRef0.current : svRef1.current
    const front = frontRef.current === 0 ? svRef0.current : svRef1.current
    if (!back) return

    if (!shownUrlRef.current) {
      back.src = url
      back.style.opacity = '1'
      frontRef.current = backIdx
      shownUrlRef.current = url
      return
    }

    shownUrlRef.current = url
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
    back.src = url
  }, [url])

  return (
    <div className={`relative overflow-hidden ${className}`}>
      <iframe
        ref={svRef0}
        title={title}
        allowFullScreen
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        className="absolute inset-0 w-full h-full border-0"
        style={{ opacity: 0, transition: 'opacity 0.4s' }}
      />
      <iframe
        ref={svRef1}
        title={`${title} 2`}
        allowFullScreen
        loading="lazy"
        referrerPolicy="no-referrer-when-downgrade"
        className="absolute inset-0 w-full h-full border-0"
        style={{ opacity: 0, pointerEvents: 'none', transition: 'opacity 0.4s' }}
      />
    </div>
  )
}
