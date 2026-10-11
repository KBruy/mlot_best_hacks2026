import { PixelButton } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { UI } from '../strings'

interface Props {
  selectedId: string | null
  onStart: () => void
}

function DemoToggle() {
  const { state, dispatch } = useGame()
  const on = state.demoMode

  return (
    <button
      type="button"
      onClick={() => dispatch({ type: 'TOGGLE_DEMO_MODE' })}
      className="flex items-center gap-2 font-mono text-xs focus-visible:outline-2 focus-visible:outline-retro-secondary"
      aria-pressed={on}
    >
      <span
        className={[
          'relative inline-flex w-9 h-5 shrink-0 border-2 transition-colors',
          on ? 'bg-retro-secondary border-retro-secondary' : 'bg-retro-surface border-retro-border-strong',
        ].join(' ')}
      >
        <span
          className={[
            'absolute top-0.5 h-3 w-3 border border-retro-bg transition-transform',
            on ? 'translate-x-4 bg-retro-bg' : 'translate-x-0.5 bg-retro-muted',
          ].join(' ')}
        />
      </span>
      <span className={on ? 'text-retro-secondary' : 'text-retro-muted'}>
        {'Tryb demo:'}
        <span className="hidden md:inline"> {on ? 'włączony' : 'wyłączony'}</span>
      </span>
    </button>
  )
}

function GpsIndicator() {
  const { state } = useGame()
  const { gpsGranted, demoMode } = state

  const label =
    gpsGranted === true
      ? UI.gps.granted
      : gpsGranted === false
        ? UI.gps.denied
        : UI.gps.unknown

  const dotClass =
    gpsGranted === true
      ? 'bg-green-500'
      : gpsGranted === false
        ? 'bg-red-500'
        : 'bg-retro-muted animate-pulse'

  return (
    <div className={['flex items-center gap-1.5 font-mono text-xs', demoMode ? 'opacity-40' : ''].join(' ')}>
      <span className={['w-2 h-2 rounded-full shrink-0', dotClass].join(' ')} />
      <span className={gpsGranted === false && !demoMode ? 'text-red-400' : 'text-retro-muted'}>
        {label}
      </span>
    </div>
  )
}

export function StartBottomBar({ selectedId, onStart }: Props) {
  const { state } = useGame()
  const { demoMode, gpsGranted } = state

  const canStart = selectedId !== null && (demoMode || gpsGranted === true)

  return (
    <div className="flex items-center justify-between gap-2 px-2 md:px-4 py-3">
      <div className="flex items-center gap-3 md:gap-4 min-w-0">
        <DemoToggle />
        <GpsIndicator />
      </div>
      <PixelButton tone="gold" disabled={!canStart} onClick={onStart}>
        {UI.start.beginButton}
      </PixelButton>
    </div>
  )
}
