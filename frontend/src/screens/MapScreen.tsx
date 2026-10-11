import { useState } from 'react'
import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { StreetViewEmbed } from '../components/StreetViewEmbed'
import { MapEmbed } from '../components/MapEmbed'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'
import { WROCLAW_LOCATIONS } from '../map/locations'
import type { MapLocation } from '../map/locations'

export function MapScreen() {
  const [active, setActive] = useState<MapLocation>(WROCLAW_LOCATIONS[0])

  return (
    <main className="min-h-screen flex flex-col items-center p-4 gap-4">
      <GameTitle className="mt-4">Miejsca legend</GameTitle>

      <div className="w-full max-w-xl flex flex-col gap-4">
        <StreetViewEmbed
          point={active.streetview}
          title={`Street View: ${active.label}`}
          className="h-64 rounded"
        />

        <div className="flex gap-2">
          <MapEmbed
            lat={active.lat}
            lon={active.lon}
            zoom={18}
            title={`Mapa: ${active.label}`}
            className="h-40 rounded flex-1"
          />
          <PixelCard title={active.label} className="flex-1">
            <NarrativeText className="text-xs">{active.description}</NarrativeText>
          </PixelCard>
        </div>

        <PixelStack gap={2}>
          {WROCLAW_LOCATIONS.map(loc => (
            <PixelButton
              key={loc.id}
              tone={active.id === loc.id ? 'gold' : 'neutral'}
              className="w-full"
              onClick={() => setActive(loc)}
            >
              {loc.label}
            </PixelButton>
          ))}
        </PixelStack>
      </div>
    </main>
  )
}
