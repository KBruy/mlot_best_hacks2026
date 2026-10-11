import { useState } from 'react'
import { StartLayout } from '../components/StartLayout'
import { StoryList } from '../components/StoryList'
import { LegendMap } from '../components/LegendMap'
import { StartBottomBar } from '../components/StartBottomBar'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  onStart: (id: string) => void
}

export function StartScreen({ summaries, onStart }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null)

  return (
    <StartLayout
      list={
        <StoryList
          summaries={summaries}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      }
      map={
        <LegendMap
          summaries={summaries}
          selectedId={selectedId}
          onSelect={setSelectedId}
        />
      }
      bottomBar={
        <StartBottomBar
          disabled={selectedId === null}
          onStart={() => { if (selectedId) onStart(selectedId) }}
        />
      }
    />
  )
}
