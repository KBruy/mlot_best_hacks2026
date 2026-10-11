import { useState, useCallback } from 'react'
import { StartLayout } from '../components/StartLayout'
import { StartPanel } from '../components/StartPanel'
import { LegendMap } from '../components/LegendMap'
import { StartBottomBar } from '../components/StartBottomBar'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  onStart: (id: string) => void
}

export function StartScreen({ summaries, onStart }: Props) {
  const [selectedId, setSelectedId] = useState<string | null>(null)
  const [focusKey, setFocusKey] = useState(0)

  const handleSelect = useCallback((id: string) => {
    setSelectedId(id)
    setFocusKey(k => k + 1)
  }, [])

  return (
    <StartLayout
      list={
        <StartPanel
          summaries={summaries}
          selectedId={selectedId}
          onSelect={handleSelect}
        />
      }
      map={
        <LegendMap
          summaries={summaries}
          selectedId={selectedId}
          focusKey={focusKey}
          onSelect={handleSelect}
        />
      }
      bottomBar={
        <StartBottomBar
          selectedId={selectedId}
          onStart={() => { if (selectedId) onStart(selectedId) }}
        />
      }
    />
  )
}
