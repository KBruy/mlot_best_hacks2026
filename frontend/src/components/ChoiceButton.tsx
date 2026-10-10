import { PixelButton } from '@pxlkit/ui-kit'

interface Props {
  children: React.ReactNode
  disabled?: boolean
  onClick: () => void
  shortcut?: number
}

export function ChoiceButton({ children, disabled = false, onClick, shortcut }: Props) {
  return (
    <PixelButton
      tone="gold"
      className="w-full text-left"
      disabled={disabled}
      onClick={onClick}
      aria-label={shortcut !== undefined ? `Opcja ${shortcut}: ${String(children)}` : undefined}
    >
      {shortcut !== undefined && (
        <span className="opacity-50 mr-2 font-mono text-xs">[{shortcut}]</span>
      )}
      {children}
    </PixelButton>
  )
}
