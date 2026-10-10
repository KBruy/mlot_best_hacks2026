import { PanelHeader } from './PanelHeader'
import { StoryListItem } from './StoryListItem'
import { UI } from '../strings'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export function StoryList({ summaries, selectedId, onSelect }: Props) {
  return (
    <div className="h-full flex flex-col bg-retro-surface">
      <PanelHeader label={UI.start.listPanel} />
      <div className="flex-1 overflow-y-auto">
        {summaries.map(s => (
          <StoryListItem
            key={s.id}
            title={s.title}
            locationName={s.location.name}
            selected={s.id === selectedId}
            onClick={() => onSelect(s.id)}
          />
        ))}
      </div>
    </div>
  )
}
