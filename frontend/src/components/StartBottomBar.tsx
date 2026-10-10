import { PixelButton } from '@pxlkit/ui-kit'
import { DemoModeToggle } from './DemoModeToggle'
import { UI } from '../strings'

interface Props {
  onStart: () => void
  disabled: boolean
}

export function StartBottomBar({ onStart, disabled }: Props) {
  return (
    <div className="flex items-center justify-between gap-4 px-4 py-3">
      <DemoModeToggle />
      <PixelButton tone="gold" disabled={disabled} onClick={onStart}>
        {UI.start.beginButton}
      </PixelButton>
    </div>
  )
}
