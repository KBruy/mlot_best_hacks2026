import { PixelButton, PixelCard } from '@pxlkit/ui-kit'
import { NarrativeText } from './NarrativeText'
import { UI } from '../strings'

interface Props {
  choiceText: string
  consequence: string
  onNext: () => void
}

export function ConsequenceView({ choiceText, consequence, onNext }: Props) {
  return (
    <PixelCard title={choiceText}>
      <NarrativeText className="mb-6">{consequence}</NarrativeText>
      <PixelButton tone="gold" className="w-full" onClick={onNext}>
        {UI.consequence.nextButton}
      </PixelButton>
    </PixelCard>
  )
}
