import { StoryList } from './StoryList'
import { PanelHeader } from './PanelHeader'
import { UI } from '../strings'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function StartPanel({ summaries, selectedId, onSelect }: Props) {
  return (
    <div className="h-full flex flex-col bg-retro-surface">
      <div className="flex-1 flex flex-col overflow-y-auto border-b-2 border-retro-border-strong">
        <div className="animate-enter px-6 pt-6 pb-5 border-b-2 border-retro-border-strong">
          <h1 className="font-mono text-retro-secondary text-xl font-bold leading-tight text-center">
            {UI.appTitle}
          </h1>
        </div>
        <div className="animate-enter-1"><PanelHeader label={UI.start.aboutLabel} /></div>
        <div className="animate-enter-2 flex flex-col gap-2 px-6 pt-5 pb-4">
          <p className="font-mono text-retro-secondary text-sm font-semibold tracking-wide">
            {UI.start.welcomeHeadline}
          </p>
          <p className="font-mono text-retro-text text-sm leading-relaxed opacity-80">
            {UI.start.welcomeBody}
          </p>
          <p className="font-mono text-retro-muted text-xs">
            {UI.start.locationHintLive}
          </p>
          <p className="font-mono text-retro-muted text-xs">
            {UI.start.locationHintDemo}
          </p>
          <p className="font-mono text-retro-muted text-xs mt-1">
            {UI.start.welcomeHint}
          </p>
        </div>
      </div>
      <div className="animate-enter-3 shrink-0" style={{ height: '52%' }}>
        <StoryList
          summaries={summaries}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      </div>
    </div>
  )
}
