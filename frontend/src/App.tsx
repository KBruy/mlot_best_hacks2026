import { useEffect } from 'react'
import { GameProvider } from './game/context'
import { useGame } from './game/useGame'
import { useGeolocation } from './map/useGeolocation'
import { LoadingScreen } from './screens/LoadingScreen'
import { ErrorScreen } from './screens/ErrorScreen'
import { StartScreen } from './screens/StartScreen'
import { SceneScreen } from './screens/SceneScreen'
import { ConsequenceScreen } from './screens/ConsequenceScreen'
import { EndingScreen } from './screens/EndingScreen'
import { MapScreen } from './screens/MapScreen'
import { fixtures } from './game/fixture'
import type { Story } from './game/types'

const isMapPage = new URLSearchParams(window.location.search).has('page') &&
  new URLSearchParams(window.location.search).get('page') === 'map'

function GameRouter() {
  const { state, dispatch } = useGame()
  useGeolocation()

  useEffect(() => {
    fetch('/api/story')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<Story>
      })
      .then(data => dispatch({ type: 'STORY_LOADED', payload: data }))
      .catch(() => dispatch({ type: 'STORY_LOADED', payload: fixtures[0] }))
  }, [dispatch])

  if (state.screen === 'loading') return <LoadingScreen />
  if (state.screen === 'error') return <ErrorScreen />
  if (state.screen === 'start') return <StartScreen stories={state.story ? [state.story] : fixtures} />
  if (state.screen === 'scene') return <SceneScreen />
  if (state.screen === 'consequence') return <ConsequenceScreen />
  if (state.screen === 'ending') return <EndingScreen />

  return null
}

function App() {
  if (isMapPage) return <MapScreen />

  return (
    <GameProvider>
      <GameRouter />
    </GameProvider>
  )
}

export default App
