import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { useGame } from '../game/context'
import type { Story } from '../game/types'

interface Props {
  stories: Story[]
}

export function StartScreen({ stories }: Props) {
  const { dispatch } = useGame()

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <h1 className="font-pixel text-retro-secondary text-center text-sm mb-2">
        Żywy Bestiariusz Wrocławia
      </h1>
      <p className="narrative text-center mb-10 text-retro-muted">
        Wybierz legendę i rozpocznij przygodę
      </p>
      <PixelStack gap="md" className="w-full max-w-xl">
        {stories.map(story => (
          <PixelCard key={story.id} title={story.title}>
            <p className="narrative mb-4 text-retro-muted">{story.intro}</p>
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
      <p className="mt-8 text-xs text-retro-muted font-mono text-center">
        Odświeżenie strony resetuje grę
      </p>
    </main>
  )
}
