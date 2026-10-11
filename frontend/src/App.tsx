import { useEffect, useState, useCallback } from 'react'
import { GameProvider } from './game/context'
import { useGame } from './game/useGame'
import { useGeolocation } from './map/useGeolocation'
import { LoadingScreen } from './screens/LoadingScreen'
import { ErrorScreen } from './screens/ErrorScreen'
import { StartScreen } from './screens/StartScreen'
import { SceneScreen } from './screens/SceneScreen'
import { WalkToStartScreen } from './screens/WalkToStartScreen'
import { ArriveScreen } from './screens/ArriveScreen'
import { ConsequenceScreen } from './screens/ConsequenceScreen'
import { EndingScreen } from './screens/EndingScreen'
import { MapScreen } from './screens/MapScreen'
import type { StorySummary, Story } from './game/types'

const isMapPage = new URLSearchParams(window.location.search).get('page') === 'map'

function GameRouter() {
  const { state, dispatch } = useGame()
  const [summaries, setSummaries] = useState<StorySummary[]>([])
  useGeolocation()

  useEffect(() => {
    fetch('/api/stories')
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<StorySummary[]>
      })
      .then(data => {
        setSummaries(data)
        dispatch({ type: 'SUMMARIES_LOADED' })
      })
      .catch((err: Error) => dispatch({ type: 'STORY_ERROR', payload: err.message }))
  }, [dispatch])

  const handleStart = useCallback((selectedId: string) => {
    fetch(`/api/stories/${selectedId}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<Story>
      })
      .then(story => dispatch({ type: 'START_STORY', payload: story }))
      .catch((err: Error) => dispatch({ type: 'STORY_ERROR', payload: err.message }))
  }, [dispatch])

  if (state.screen === 'loading') return <LoadingScreen />
  if (state.screen === 'error') return <ErrorScreen />
  if (state.screen === 'start') return <StartScreen summaries={summaries} onStart={handleStart} />
  if (state.screen === 'walk_to_start') return <WalkToStartScreen />
  if (state.screen === 'scene') return <SceneScreen />
  if (state.screen === 'arrive') return <ArriveScreen />
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
