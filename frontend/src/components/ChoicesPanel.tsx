import { PixelStack } from '@pxlkit/ui-kit'
import { PanelHeader } from './PanelHeader'
import { ChoiceButton } from './ChoiceButton'
import { UI } from '../strings'
import { resolveText } from '../game/textUtils'
import type { Option, GameFields } from '../game/types'

interface Props {
  options: Option[]
  fields: GameFields
  onSelect: (option: Option) => void
  locked: boolean
}

export function ChoicesPanel({ options, fields, onSelect, locked }: Props) {
  return (
    <div className="w-full h-full flex flex-col border-t-2 border-retro-border-strong bg-retro-surface">
      <PanelHeader label={UI.scene.panelChoices} />
      <div className="flex-1 overflow-y-auto p-4">
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
      </div>
    </div>
  )
}
