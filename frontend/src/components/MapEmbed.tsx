interface Props {
  lat: number
  lon: number
  zoom?: number
  title: string
  className?: string
}

function mapUrl(lat: number, lon: number, zoom: number): string {
  return `https://maps.google.com/maps?q=${lat},${lon}&z=${zoom}&t=k&output=embed`
}

export function MapEmbed({ lat, lon, zoom = 18, title, className = '' }: Props) {
  return (
    <iframe
      src={mapUrl(lat, lon, zoom)}
      title={title}
      allowFullScreen
      loading="lazy"
      referrerPolicy="no-referrer-when-downgrade"
      className={`w-full border-0 ${className}`}
    />
  )
}
