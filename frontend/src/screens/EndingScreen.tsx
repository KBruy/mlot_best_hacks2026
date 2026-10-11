import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { EndingFlow } from '../components/EndingFlow'

export function EndingScreen() {
  const { state, dispatch } = useGame()

  if (!state.story || !state.currentSceneId) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <EndingFlow
          endingKey={state.currentSceneId}
          story={state.story}
          fields={state.gameFields}
          legendScore={state.legendScore}
          onRestart={() => dispatch({ type: 'RESTART' })}
        />
      </div>
    </GameLayout>
  )
}
