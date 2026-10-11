interface Props {
  title: string
  locationName: string
  teaser: string | null
  selected: boolean
  onClick: () => void
}

export function StoryListItem({ title, locationName, teaser, selected, onClick }: Props) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={[
        'w-full text-left px-4 py-3 border-2 transition-colors focus-visible:outline-2 focus-visible:outline-retro-secondary',
        selected
          ? 'border-retro-secondary bg-retro-card'
          : 'border-retro-border bg-retro-surface hover:border-retro-border-strong hover:bg-retro-card',
      ].join(' ')}
    >
      <div className="font-mono text-retro-secondary text-sm leading-snug">{title}</div>
      <div className="font-mono text-retro-muted text-xs mt-1">
        <span className="text-retro-border-strong uppercase tracking-widest text-[10px]">Start: </span>
        {locationName}
      </div>
      {teaser && (
        <div className="font-mono text-retro-text text-xs mt-2 leading-relaxed opacity-70 line-clamp-2">
          {teaser}
        </div>
      )}
    </button>
  )
}
