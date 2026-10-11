interface Props {
  list: React.ReactNode
  map: React.ReactNode
  bottomBar: React.ReactNode
}

export function StartLayout({ list, map, bottomBar }: Props) {
  return (
    <div className="h-screen flex flex-col overflow-hidden border-2 border-retro-border-strong">
      <div className="flex-1 flex flex-col md:flex-row min-h-0">
        <div className="flex-1 md:flex-none md:h-full md:w-1/2 min-h-0 overflow-hidden border-b-2 md:border-b-0 md:border-r-2 border-retro-border-strong">
          {list}
        </div>
        <div className="flex-1 md:flex-none md:h-full md:w-1/2 min-h-0 overflow-hidden">
          {map}
        </div>
      </div>
      <div className="shrink-0 border-t-2 border-retro-border-strong bg-retro-surface">
        {bottomBar}
      </div>
    </div>
  )
}
