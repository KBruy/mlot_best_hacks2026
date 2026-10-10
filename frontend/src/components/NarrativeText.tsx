interface Props {
  children: React.ReactNode
  className?: string
  center?: boolean
}

export function NarrativeText({ children, className = '', center = false }: Props) {
  return (
    <p className={`narrative text-retro-muted ${center ? 'text-center' : ''} ${className}`}>
      {children}
    </p>
  )
}
