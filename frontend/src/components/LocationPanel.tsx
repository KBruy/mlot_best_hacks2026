import { PanelHeader } from './PanelHeader'
import { StreetViewEmbed } from './StreetViewEmbed'
import { NarrativeText } from './NarrativeText'
import { UI } from '../strings'
import type { StreetViewShot } from '../game/types'

interface Props {
  shot?: StreetViewShot | null
  label?: string
}

export function LocationPanel({ shot, label }: Props) {
  return (
    <div className="h-full flex flex-col border-b-2 md:border-b-0 border-retro-border-strong bg-retro-bg">
      <PanelHeader label={label ?? UI.scene.panelLocation} />
      <div className="flex-1 overflow-hidden">
        {shot ? (
          <StreetViewEmbed point={shot} title={label ?? UI.scene.panelLocation} className="h-full" />
        ) : (
          <div className="h-full flex items-center justify-center">
            <NarrativeText center className="opacity-20">Wrocław</NarrativeText>
          </div>
        )}
      </div>
    </div>
  )
}
