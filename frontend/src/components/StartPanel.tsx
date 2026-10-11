import { StoryList } from './StoryList'
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
      <div className="flex-1 flex flex-col gap-3 px-6 pt-6 pb-4 overflow-y-auto border-b-2 border-retro-border-strong">
        <h1 className="font-mono text-retro-secondary text-xl font-bold leading-tight text-center">
          {UI.appTitle}
        </h1>
        <p className="text-retro-secondary text-sm font-semibold tracking-wide">
          {UI.start.welcomeHeadline}
        </p>
        <p className="text-retro-text text-sm leading-relaxed opacity-80">
          {UI.start.welcomeBody}
        </p>
        <p className="text-retro-muted text-xs mt-1">
          {UI.start.welcomeHint}
        </p>
      </div>
      <div className="shrink-0" style={{ height: '52%' }}>
        <StoryList
          summaries={summaries}
          selectedId={selectedId}
          onSelect={onSelect}
        />
      </div>
    </div>
  )
}
