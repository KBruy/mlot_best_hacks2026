interface Props {
  label: string
}

export function PanelHeader({ label }: Props) {
  return (
    <div className="flex items-center gap-2 px-3 py-1 bg-retro-card border-b-2 border-retro-border-strong shrink-0">
      <span className="font-pixel text-retro-secondary text-xs tracking-widest">{label}</span>
      <div className="flex-1 h-px bg-retro-border-strong opacity-50" />
    </div>
  )
}
