import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { GameTitle } from '../components/GameTitle'
import { NarrativeText } from '../components/NarrativeText'
import { HintText } from '../components/HintText'
import type { Story } from '../game/types'

interface Props {
  stories: Story[]
}

export function StartScreen({ stories }: Props) {
  const { dispatch } = useGame()

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <GameTitle className="mb-2">Żywy Bestiariusz Wrocławia</GameTitle>
      <NarrativeText center className="mb-10">Wybierz legendę i rozpocznij przygodę</NarrativeText>
      <PixelStack gap={4} className="w-full max-w-xl">
        {stories.map(story => (
          <PixelCard key={story.id} title={story.title}>
            <NarrativeText className="mb-4">{story.intro}</NarrativeText>
            <PixelButton
              tone="gold"
              className="w-full"
              onClick={() => dispatch({ type: 'START_STORY', payload: story })}
            >
              Rozpocznij
            </PixelButton>
          </PixelCard>
        ))}
      </PixelStack>
      <HintText className="mt-8">Odświeżenie strony resetuje grę</HintText>
    </main>
  )
}
