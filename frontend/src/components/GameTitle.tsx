interface Props {
  children: React.ReactNode
  className?: string
}

export function GameTitle({ children, className = '' }: Props) {
  return (
    <h1 className={`font-pixel text-retro-secondary text-center text-sm leading-relaxed mb-2 ${className}`}>
      {children}
    </h1>
  )
}
