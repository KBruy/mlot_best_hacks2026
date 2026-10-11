import { StreetViewEmbed } from './StreetViewEmbed'
import { NarrativeText } from './NarrativeText'
import { UI } from '../strings'
import type { StreetViewShot } from '../game/types'

interface Props {
  shot?: StreetViewShot | null
  label?: string
  onBack?: () => void
}

export function LocationPanel({ shot, label, onBack }: Props) {
  return (
    <div className="h-full flex flex-col border-b-2 md:border-b-0 border-retro-border-strong bg-retro-bg">
      <div className="flex items-center gap-2 px-3 py-1 bg-retro-card border-b-2 border-retro-border-strong shrink-0">
        <div className="flex-1 h-px bg-retro-border-strong opacity-50" />
        <span className="text-retro-secondary text-xs tracking-widest">{label ?? UI.scene.panelLocation}</span>
        <div className="flex-1 h-px bg-retro-border-strong opacity-50" />
        {onBack && (
          <button
            onClick={onBack}
            className="text-retro-muted text-xs hover:text-retro-secondary shrink-0 px-1"
            aria-label="Nowa gra"
          >
            ✕
          </button>
        )}
      </div>
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
