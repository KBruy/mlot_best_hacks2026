import { useEffect, useCallback } from 'react'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { ConsequenceView } from '../components/ConsequenceView'
import { resolveParagraphs, resolveText } from '../game/textUtils'

export function ConsequenceScreen() {
  const { state, dispatch } = useGame()

  const advance = useCallback(() => {
    dispatch({ type: 'ADVANCE_SCENE' })
  }, [dispatch])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.code === 'Enter' || e.code === 'Space') {
        e.preventDefault()
        advance()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [advance])

  if (!state.pendingOption) return null

  const choiceText = resolveText(state.pendingOption.text, state.gameFields) ?? ''
  const result = resolveParagraphs(state.pendingOption.result, state.gameFields)

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <ConsequenceView
          choiceText={choiceText}
          result={result}
          onNext={advance}
        />
      </div>
    </GameLayout>
  )
}
