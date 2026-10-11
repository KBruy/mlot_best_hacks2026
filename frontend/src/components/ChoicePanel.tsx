import { PixelStack } from '@pxlkit/ui-kit'
import { ChoiceButton } from './ChoiceButton'
import { resolveText } from '../game/textUtils'
import type { Option, GameFields } from '../game/types'

interface Props {
  options: Option[]
  fields: GameFields
  onSelect: (option: Option) => void
  locked: boolean
}

export function ChoicePanel({ options, fields, onSelect, locked }: Props) {
  return (
    <PixelStack gap={2}>
      {options.map((option, index) => (
        <ChoiceButton
          key={index}
          disabled={locked}
          onClick={() => onSelect(option)}
          shortcut={index + 1}
        >
          {resolveText(option.text, fields) ?? ''}
        </ChoiceButton>
      ))}
    </PixelStack>
  )
}
