import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { UI } from '../strings'

interface Props {
  choiceText: string
  result: string[]
  onNext: () => void
}

export function ConsequenceView({ choiceText, result, onNext }: Props) {
  return (
    <PixelCard title={choiceText}>
      {result.map((paragraph, i) => (
        <NarrativeText key={i} className="mb-3">{paragraph}</NarrativeText>
      ))}
      <PixelButton tone="gold" className="w-full mt-3" onClick={onNext}>
        {UI.consequence.nextButton}
      </PixelButton>
    </PixelCard>
  )
}
