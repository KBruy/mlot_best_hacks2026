interface Props {
  story: React.ReactNode
  location: React.ReactNode
  choices: React.ReactNode
}

export function SceneLayout({ story, location, choices }: Props) {
  return (
    <div className="h-screen overflow-hidden border-2 border-retro-border-strong grid [grid-template-areas:'location'_'story'_'choices'] grid-rows-[35vh_1fr_25vh] grid-cols-1 md:[grid-template-areas:'story_location'_'choices_choices'] md:grid-rows-[70vh_30vh] md:grid-cols-[35%_65%]">
      <div className="[grid-area:story] min-h-0 overflow-hidden">
        {story}
      </div>
      <div className="[grid-area:location] min-h-0 overflow-hidden">
        {location}
      </div>
      <div className="[grid-area:choices] min-h-0 overflow-hidden">
        {choices}
      </div>
    </div>
  )
}
