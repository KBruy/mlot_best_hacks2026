import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameLayout } from '../components/GameLayout'
import { NarrativeText } from '../components/NarrativeText'
import { UI } from '../strings'

export function ArriveScreen() {
  const { state, dispatch } = useGame()

  const scene = state.currentSceneId ? state.story?.scenes[state.currentSceneId] ?? null : null
  const stop = scene?.before ? state.story?.stops[scene.before] ?? null : null

  if (!stop) return null

  return (
    <GameLayout>
      <div className="w-full max-w-xl">
        <PixelCard title={stop.label}>
          <NarrativeText className="mb-4">{stop.arrive}</NarrativeText>
          <PixelButton
            tone="gold"
            className="w-full"
            onClick={() => dispatch({ type: 'DISMISS_ARRIVAL' })}
          >
            {UI.consequence.nextButton}
          </PixelButton>
        </PixelCard>
      </div>
    </GameLayout>
  )
}
