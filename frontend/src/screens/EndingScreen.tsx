import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeText } from '../components/NarrativeText'
import { HintText } from '../components/HintText'
import { resolveParagraphs } from '../game/textUtils'
import { UI } from '../strings'

export function EndingScreen() {
  const { state, dispatch } = useGame()

  const ending = state.currentSceneId ? state.story?.endings[state.currentSceneId] ?? null : null
  if (!ending) return null

  const paragraphs = resolveParagraphs(ending.paragraphs, state.gameFields)

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <HintText className="mb-4">{UI.ending.hint}</HintText>
        <PixelCard title={ending.title}>
          {paragraphs.map((p, i) => (
            <NarrativeText key={i} className="mb-3">{p}</NarrativeText>
          ))}
          <PixelButton
            tone="gold"
            className="w-full mt-3"
            onClick={() => dispatch({ type: 'RESTART' })}
          >
            {UI.ending.restartButton}
          </PixelButton>
        </PixelCard>
      </div>
    </GameLayout>
  )
}
