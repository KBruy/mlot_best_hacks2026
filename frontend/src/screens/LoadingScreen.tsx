import { GameLayout } from '../components/GameLayout'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'
import { UI } from '../strings'

export function LoadingScreen() {
  return (
    <GameLayout>
      <GameTitle>{UI.appTitle}</GameTitle>
      <NarrativeText center>{UI.loading.message}</NarrativeText>
    </GameLayout>
  )
}
