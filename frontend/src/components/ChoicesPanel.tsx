import { PixelStack } from '@pxlkit/ui-kit'
import { PanelHeader } from './PanelHeader'
import { ChoiceButton } from './ChoiceButton'
import { UI } from '../strings'
import type { Choice } from '../game/types'

interface Props {
  choices: Choice[]
  onSelect: (choice: Choice) => void
  locked: boolean
}

export function ChoicesPanel({ choices, onSelect, locked }: Props) {
  return (
    <div className="w-full h-full flex flex-col border-t-2 border-retro-border-strong bg-retro-surface">
      <PanelHeader label={UI.scene.panelChoices} />
      <div className="flex-1 overflow-y-auto p-4">
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
      </div>
    </div>
  )
}
