import { PixelButton, PixelCard, PixelStack } from '@pxlkit/ui-kit'
import { GameTitle } from '../components/GameTitle'
import { HintText } from '../components/HintText'
import { DemoModeToggle } from '../components/DemoModeToggle'
import { UI } from '../strings'
import type { StorySummary } from '../game/types'

interface Props {
  summaries: StorySummary[]
  onStart: (id: string) => void
}

export function StartScreen({ summaries, onStart }: Props) {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      <GameTitle className="mb-8">{UI.appTitle}</GameTitle>
      <PixelStack gap={4} className="w-full max-w-xl">
        {summaries.map(s => (
          <PixelCard key={s.id} title={s.title}>
            <HintText className="mb-4">{s.location.name}</HintText>
            <PixelButton tone="gold" className="w-full" onClick={() => onStart(s.id)}>
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
