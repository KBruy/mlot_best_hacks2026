import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'
import { HintText } from '../components/HintText'
import { DemoModeToggle } from '../components/DemoModeToggle'
import { UI } from '../strings'
import type { Story } from '../game/types'

interface Props {
  stories: Story[]
}

export function StartScreen({ stories }: Props) {
  const { dispatch } = useGame()

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <GameTitle className="mb-2">{UI.appTitle}</GameTitle>
      <NarrativeText center className="mb-10">{UI.start.subtitle}</NarrativeText>
      <PixelStack gap={4} className="w-full max-w-xl">
        {stories.map(story => (
          <PixelCard key={story.id} title={story.title}>
            <NarrativeText className="mb-4">{story.intro}</NarrativeText>
            <PixelButton
              tone="gold"
              className="w-full"
              onClick={() => dispatch({ type: 'START_STORY', payload: story })}
            >
              {UI.start.beginButton}
            </PixelButton>
          </PixelCard>
        ))}
      </PixelStack>
      <div className="mt-8">
        <DemoModeToggle />
      </div>
      <HintText className="mt-4">{UI.start.resetHint}</HintText>
    </main>
  )
}
