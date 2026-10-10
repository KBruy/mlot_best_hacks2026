import { PanelHeader } from './PanelHeader'
import { StreetViewEmbed } from './StreetViewEmbed'
import { NarrativeText } from './NarrativeText'
import { UI } from '../strings'
import type { NodeLocation } from '../game/types'

interface Props {
  location?: NodeLocation
}

export function LocationPanel({ location }: Props) {
  return (
    <div className="h-full flex flex-col border-b-2 md:border-b-0 border-retro-border-strong bg-retro-bg">
      <PanelHeader label={location?.label ?? UI.scene.panelLocation} />
      <div className="flex-1 overflow-hidden">
        {location ? (
          <StreetViewEmbed
            point={location.streetview}
            title={location.label}
            className="h-full"
          />
        ) : (
          <div className="h-full flex items-center justify-center">
            <NarrativeText center className="opacity-20">
              {/* TODO: po kontrakcie — Street View bieżącej lokalizacji z GPS */}
              Wrocław
            </NarrativeText>
          </div>
        )}
      </div>
    </div>
  )
}
