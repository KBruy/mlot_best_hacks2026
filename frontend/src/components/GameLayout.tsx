interface Props {
  children: React.ReactNode
}

export function GameLayout({ children }: Props) {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4">
      {children}
    </main>
  )
}
