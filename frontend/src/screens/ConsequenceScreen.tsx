import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { ConsequenceView } from '../components/ConsequenceView'

export function ConsequenceScreen() {
  const { state, dispatch } = useGame()

  if (!state.pendingChoice) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <ConsequenceView
          choiceText={state.pendingChoice.text}
          consequence={state.pendingChoice.consequence}
          onNext={() => dispatch({ type: 'ADVANCE_SCENE' })}
        />
      </div>
    </GameLayout>
  )
}
