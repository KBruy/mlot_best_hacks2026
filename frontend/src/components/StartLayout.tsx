interface Props {
  list: React.ReactNode
  map: React.ReactNode
  bottomBar: React.ReactNode
}

export function StartLayout({ list, map, bottomBar }: Props) {
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <div className="flex-1 flex flex-col md:flex-row min-h-0">
        <div className="h-1/2 md:h-full md:w-1/2 border-b-2 md:border-b-0 md:border-r-2 border-retro-border-strong overflow-hidden">
          {list}
        </div>
        <div className="h-1/2 md:h-full md:w-1/2 overflow-hidden">
          {map}
        </div>
      </div>
      <div className="shrink-0 border-t-2 border-retro-border-strong bg-retro-surface">
        {bottomBar}
      </div>
    </div>
  )
}
