import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeText } from '../components/NarrativeText'
import { UI } from '../strings'

export function ConsequenceScreen() {
  const { state, dispatch } = useGame()

  if (!state.pendingChoice) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <PixelCard title={state.pendingChoice.text}>
          <NarrativeText className="mb-6">{state.pendingChoice.consequence}</NarrativeText>
          <PixelButton
            tone="gold"
            className="w-full"
            onClick={() => dispatch({ type: 'ADVANCE_SCENE' })}
          >
            {UI.consequence.nextButton}
          </PixelButton>
        </PixelCard>
      </div>
    </GameLayout>
  )
}
