import { useState, useEffect, useCallback } from 'react'
import { useGame } from '../game/useGame'
import { useLocationGate } from '../map/useLocationGate'
import { SceneLayout } from '../components/SceneLayout'
import { StoryPanel } from '../components/StoryPanel'
import { LocationPanel } from '../components/LocationPanel'
import { ChoicesPanel } from '../components/ChoicesPanel'
import { LocationGate } from '../components/LocationGate'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { HintText } from '../components/HintText'
import { UI } from '../strings'
import type { Choice, DecisionNode } from '../game/types'

export function SceneScreen() {
  const { state, dispatch } = useGame()
  const [completedNodeId, setCompletedNodeId] = useState<string | null>(null)

  const node = state.story?.nodes.find(n => n.id === state.currentNodeId)
  const decisionNode = node?.type === 'decision' ? (node as DecisionNode) : null

  const { blocked, distanceM } = useLocationGate(
    decisionNode ?? { id: '', type: 'decision', text: '', choices: [] },
  )

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

  if (blocked) {
    return (
      <GameLayout>
        <div className="w-full max-w-xl">
          <HintText className="mb-4">
            {UI.scene.decisionHint(state.decisionCount + 1, UI.scene.totalDecisions)}
          </HintText>
          <LocationGate location={decisionNode.location!} distanceM={distanceM} />
        </div>
      </GameLayout>
    )
  }

  return (
    <SceneLayout
      story={
        <StoryPanel>
          <HintText className="mb-4">
            {UI.scene.decisionHint(state.decisionCount + 1, UI.scene.totalDecisions)}
          </HintText>
          <NarrativeKaraoke
            key={state.currentNodeId ?? undefined}
            text={decisionNode.text}
            onComplete={handleKaraokeComplete}
          />
        </StoryPanel>
      }
      location={<LocationPanel location={decisionNode.location} />}
      choices={
        <ChoicesPanel
          choices={decisionNode.choices}
          onSelect={handleSelect}
          locked={choicesLocked}
        />
      }
    />
  )
}
