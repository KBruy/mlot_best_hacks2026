import { GameLayout } from '../components/GameLayout'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'

export function LoadingScreen() {
  return (
    <GameLayout>
      <GameTitle>Żywy Bestiariusz Wrocławia</GameTitle>
      <NarrativeText center>Ładowanie legendy…</NarrativeText>
    </GameLayout>
  )
}
