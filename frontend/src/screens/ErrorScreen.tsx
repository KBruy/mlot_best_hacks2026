import { PixelButton } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'

export function ErrorScreen() {
  const { state, dispatch } = useGame()

  return (
    <GameLayout>
      <GameTitle>Błąd połączenia</GameTitle>
      <NarrativeText center className="mb-2">
        Nie udało się pobrać historii z serwera.
      </NarrativeText>
      {state.errorMessage && (
        <NarrativeText center className="mb-6 text-xs">
          {state.errorMessage}
        </NarrativeText>
      )}
      <PixelButton tone="gold" onClick={() => dispatch({ type: 'RETRY_FETCH' })}>
        Spróbuj ponownie
      </PixelButton>
    </GameLayout>
  )
}
