import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeText } from '../components/NarrativeText'
import { HintText } from '../components/HintText'
import { UI } from '../strings'
import type { EndingNode } from '../game/types'

export function EndingScreen() {
  const { state, dispatch } = useGame()

  const node = state.story?.nodes.find(n => n.id === state.currentNodeId)
  if (!node || node.type !== 'ending') return null

  const endingNode = node as EndingNode

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <HintText className="mb-4">{UI.ending.hint}</HintText>
        <PixelCard title={endingNode.title}>
          <NarrativeText className="mb-6">{endingNode.text}</NarrativeText>
          <PixelButton
            tone="gold"
            className="w-full"
            onClick={() => dispatch({ type: 'RESTART' })}
          >
            {UI.ending.restartButton}
          </PixelButton>
        </PixelCard>
      </div>
    </GameLayout>
  )
}
