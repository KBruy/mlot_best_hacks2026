import { PixelButton } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'
import { UI } from '../strings'

export function ErrorScreen() {
  const { state, dispatch } = useGame()

  return (
    <GameLayout>
      <GameTitle>{UI.error.title}</GameTitle>
      <NarrativeText center className="mb-2">
        {UI.error.message}
      </NarrativeText>
      {state.errorMessage && (
        <NarrativeText center className="mb-6 text-xs">
          {state.errorMessage}
        </NarrativeText>
      )}
      <PixelButton tone="gold" onClick={() => dispatch({ type: 'RETRY_FETCH' })}>
        {UI.error.retryButton}
      </PixelButton>
    </GameLayout>
  )
}
