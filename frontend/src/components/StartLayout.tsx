import { useState } from 'react'

interface Props {
  list: React.ReactNode
  map: React.ReactNode
  bottomBar: React.ReactNode
}

type MobileTab = 'list' | 'map'

export function StartLayout({ list, map, bottomBar }: Props) {
  const [mobileTab, setMobileTab] = useState<MobileTab>('list')
  // On desktop the map is always in DOM; on mobile mount it lazily (first open)
  const [mapMounted, setMapMounted] = useState(
    () => typeof window !== 'undefined' && window.innerWidth >= 768,
  )

  function handleMapTab() {
    if (!mapMounted) setMapMounted(true)
    setMobileTab('map')
  }

  function tabClass(active: boolean, border?: 'right') {
    return [
      'flex-1 py-2 font-mono text-sm font-bold transition-colors',
      border === 'right' ? 'border-r-2 border-retro-border-strong' : '',
      active
        ? 'bg-retro-secondary text-retro-bg'
        : 'bg-retro-surface text-retro-muted',
    ].join(' ')
  }

  return (
    <div className="h-dvh flex flex-col overflow-hidden border-2 border-retro-border-strong">
      {/* Mobile-only tab bar */}
      <div className="md:hidden flex shrink-0 border-b-2 border-retro-border-strong">
        <button type="button" className={tabClass(mobileTab === 'list', 'right')} onClick={() => setMobileTab('list')}>
          Lista
        </button>
        <button type="button" className={tabClass(mobileTab === 'map')} onClick={handleMapTab}>
          Mapa
        </button>
      </div>

      <div className="flex-1 flex flex-col md:flex-row min-h-0">
        {/* List panel */}
        <div className={[
          'min-h-0 overflow-hidden',
          'md:flex-none md:h-full md:w-1/2 md:border-r-2 md:border-retro-border-strong',
          mobileTab === 'list' ? 'flex-1' : 'hidden md:block',
        ].join(' ')}>
          {list}
        </div>
        {/* Map panel — hidden on mobile until user opens map tab */}
        <div className={[
          'min-h-0 overflow-hidden isolate',
          'md:flex-none md:h-full md:w-1/2',
          mobileTab === 'map' ? 'flex-1' : 'hidden md:block',
        ].join(' ')}>
          {mapMounted && map}
        </div>
      </div>

      <div className="animate-enter-5 shrink-0 border-t-2 border-retro-border-strong bg-retro-surface">
        {bottomBar}
      </div>
    </div>
  )
}
