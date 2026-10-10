import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeText } from '../components/NarrativeText'
import { HintText } from '../components/HintText'
import type { DecisionNode } from '../game/types'

export function SceneScreen() {
  const { state, dispatch } = useGame()

  const node = state.story?.nodes.find(n => n.id === state.currentNodeId)
  if (!node || node.type !== 'decision') return null

  const decisionNode = node as DecisionNode

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <HintText className="mb-4">
          Decyzja {state.decisionCount + 1} z 6
        </HintText>
        <PixelCard title={state.story?.title ?? ''}>
          <NarrativeText className="mb-6">{decisionNode.text}</NarrativeText>
          <PixelStack gap={2}>
            {decisionNode.choices.map(choice => (
              <PixelButton
                key={choice.id}
                tone="gold"
                className="w-full"
                disabled={state.choiceLocked}
                onClick={() => dispatch({ type: 'SELECT_CHOICE', payload: choice })}
              >
                {choice.text}
              </PixelButton>
            ))}
          </PixelStack>
        </PixelCard>
      </div>
    </GameLayout>
  )
}
