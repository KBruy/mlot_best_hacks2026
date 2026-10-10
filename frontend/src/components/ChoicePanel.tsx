import { PixelStack } from '@pxlkit/ui-kit'
import { ChoiceButton } from './ChoiceButton'
import type { Choice } from '../game/types'

interface Props {
  choices: Choice[]
  onSelect: (choice: Choice) => void
  locked: boolean
}

export function ChoicePanel({ choices, onSelect, locked }: Props) {
  return (
    <PixelStack gap={2}>
      {choices.map((choice, index) => (
        <ChoiceButton
          key={choice.id}
          disabled={locked}
          onClick={() => onSelect(choice)}
          shortcut={index + 1}
        >
          {choice.text}
        </ChoiceButton>
      ))}
    </PixelStack>
  )
}
