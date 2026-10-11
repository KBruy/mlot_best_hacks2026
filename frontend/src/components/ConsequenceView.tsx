import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { NarrativeKaraoke } from './NarrativeKaraoke'
import { UI } from '../strings'
import type { Variant } from '../game/types'

interface Props {
  choiceText: string
  result: Variant[]
  onNext: () => void
}

export function ConsequenceView({ choiceText, result, onNext }: Props) {
  return (
    <PixelCard title={choiceText}>
      <NarrativeKaraoke paragraphs={result} />
      <PixelButton tone="gold" className="w-full mt-3" onClick={onNext}>
        {UI.consequence.nextButton}
      </PixelButton>
    </PixelCard>
  )
}
