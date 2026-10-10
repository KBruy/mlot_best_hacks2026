interface Props {
  story: React.ReactNode
  location: React.ReactNode
  choices: React.ReactNode
}

export function SceneLayout({ story, location, choices }: Props) {
  return (
    <div className="h-screen flex flex-col overflow-hidden border-2 border-retro-border-strong">
      <div className="flex h-[70vh] min-h-0">
        {story}
        {location}
      </div>
      <div className="h-[30vh] min-h-0">
        {choices}
      </div>
    </div>
  )
}
