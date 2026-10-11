export interface MapLocation {
  id: string
  label: string
  description: string
  lat: number
  lon: number
  streetview: {
    lat: number
    lon: number
    heading: number
    pitch: number
  }
}

export const WROCLAW_LOCATIONS: MapLocation[] = [
  {
    id: 'mostek',
    label: 'Mostek Czarownic',
    description: 'Mostek między wieżami, na którym zamiatała Tekla',
    lat: 51.109652,
    lon: 17.034396,
    streetview: { lat: 51.109652, lon: 17.034396, heading: 290, pitch: 10 },
  },
  {
    id: 'wieze',
    label: 'Wieże kościoła',
    description: 'Kościół św. Marii Magdaleny — dwie ceglane wieże',
    lat: 51.109666,
    lon: 17.034503,
    streetview: { lat: 51.109593, lon: 17.034374, heading: 85, pitch: -60 },
  },
  {
    id: 'rynek',
    label: 'Rynek — pręgierz',
    description: 'Miejsce spotkania z czarodziejem Michałem',
    lat: 51.1094653,
    lon: 17.0327099,
    streetview: { lat: 51.109626, lon: 17.032965, heading: 215, pitch: 0 },
  },
]
