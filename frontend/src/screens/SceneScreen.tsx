import { useState, useEffect, useCallback } from 'react'
import { PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { ChoicePanel } from '../components/ChoicePanel'
import { HintText } from '../components/HintText'
import { UI } from '../strings'
import type { Choice, DecisionNode } from '../game/types'

export function SceneScreen() {
  const { state, dispatch } = useGame()
  const [completedNodeId, setCompletedNodeId] = useState<string | null>(null)

  const node = state.story?.nodes.find(n => n.id === state.currentNodeId)
  const decisionNode = node?.type === 'decision' ? (node as DecisionNode) : null

  const karaokeComplete = completedNodeId === state.currentNodeId
  const choicesLocked = !karaokeComplete || state.choiceLocked

  const handleKaraokeComplete = useCallback(() => {
    setCompletedNodeId(state.currentNodeId)
  }, [state.currentNodeId])

  const handleSelect = useCallback((choice: Choice) => {
    dispatch({ type: 'SELECT_CHOICE', payload: choice })
  }, [dispatch])

  useEffect(() => {
    if (!decisionNode || choicesLocked) return
    const handleKey = (e: KeyboardEvent) => {
      const index = parseInt(e.key) - 1
      if (index >= 0 && index < decisionNode.choices.length) {
        handleSelect(decisionNode.choices[index])
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [choicesLocked, decisionNode, handleSelect])

  if (!decisionNode) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <HintText className="mb-4">
          {UI.scene.decisionHint(state.decisionCount + 1, UI.scene.totalDecisions)}
        </HintText>
        <PixelCard title={state.story?.title ?? ''}>
          <NarrativeKaraoke
            key={state.currentNodeId ?? undefined}
            text={decisionNode.text}
            onComplete={handleKaraokeComplete}
            className="mb-6"
          />
          <ChoicePanel
            choices={decisionNode.choices}
            onSelect={handleSelect}
            locked={choicesLocked}
          />
        </PixelCard>
      </div>
    </GameLayout>
  )
}
