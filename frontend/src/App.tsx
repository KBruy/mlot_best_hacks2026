import { GameProvider } from './game/context'
import { StartScreen } from './screens/StartScreen'
import { fixtures } from './game/fixture'

function App() {
  return (
    <GameProvider>
      <StartScreen stories={fixtures} />
    </GameProvider>
  )
}

export default App
