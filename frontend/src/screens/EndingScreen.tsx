import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { HintText } from '../components/HintText'
import { resolveParagraphs } from '../game/textUtils'
import { UI } from '../strings'
import { EndingFlow } from '../components/EndingFlow'

export function EndingScreen() {
  const { state, dispatch } = useGame()

  if (!state.story || !state.currentSceneId) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <HintText className="mb-4">{UI.ending.hint}</HintText>
        <PixelCard title={ending.title}>
          <NarrativeKaraoke paragraphs={paragraphs} />
          <PixelButton
            tone="gold"
            className="w-full mt-3"
            onClick={() => dispatch({ type: 'RESTART' })}
          >
            {UI.ending.restartButton}
          </PixelButton>
        </PixelCard>
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
