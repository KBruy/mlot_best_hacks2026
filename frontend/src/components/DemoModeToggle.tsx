import { PixelButton } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { UI } from '../strings'

export function DemoModeToggle() {
  const { state, dispatch } = useGame()

  return (
    <PixelButton
      tone={state.demoMode ? 'green' : 'neutral'}
      onClick={() => dispatch({ type: 'TOGGLE_DEMO_MODE' })}
    >
      {state.demoMode ? UI.demo.on : UI.demo.off}
    </PixelButton>
  )
}
