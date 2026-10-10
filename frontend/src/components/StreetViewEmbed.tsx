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
  return (
    <iframe
      src={svUrl(point)}
      title={title}
      allowFullScreen
      loading="lazy"
      referrerPolicy="no-referrer-when-downgrade"
      className={`w-full border-0 ${className}`}
    />
  )
}
