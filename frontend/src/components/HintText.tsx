interface Props {
  children: React.ReactNode
  className?: string
}

export function HintText({ children, className = '' }: Props) {
  return (
    <p className={`text-xs font-mono text-retro-muted text-center ${className}`}>
      {children}
    </p>
  )
}
