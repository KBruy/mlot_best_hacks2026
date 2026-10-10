import { PanelHeader } from './PanelHeader'
import { UI } from '../strings'

interface Props {
  children: React.ReactNode
}

export function StoryPanel({ children }: Props) {
  return (
    <div className="h-full flex flex-col md:border-r-2 border-retro-border-strong bg-retro-surface">
      <PanelHeader label={UI.scene.panelStory} />
      <div className="flex-1 overflow-y-auto p-6">
        {children}
      </div>
    </div>
  )
}
