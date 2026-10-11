import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { ConsequenceView } from '../components/ConsequenceView'
import { resolveParagraphs, resolveText } from '../game/textUtils'

export function ConsequenceScreen() {
  const { state, dispatch } = useGame()

  if (!state.pendingOption) return null

  const choiceText = resolveText(state.pendingOption.text, state.gameFields) ?? ''
  const result = resolveParagraphs(state.pendingOption.result, state.gameFields)

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <ConsequenceView
          choiceText={choiceText}
          result={result}
          onNext={() => dispatch({ type: 'ADVANCE_SCENE' })}
        />
      </div>
    </GameLayout>
  )
}
