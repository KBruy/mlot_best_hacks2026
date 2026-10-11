import { useState, useEffect, useCallback } from 'react'
import { useGame } from '../game/useGame'
import { useLocationGate } from '../map/useLocationGate'
import { resolveParagraphs } from '../game/textUtils'
import { SceneLayout } from '../components/SceneLayout'
import { StoryPanel } from '../components/StoryPanel'
import { LocationPanel } from '../components/LocationPanel'
import { ChoicesPanel } from '../components/ChoicesPanel'
import { LocationGate } from '../components/LocationGate'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { UI } from '../strings'
import type { Option } from '../game/types'

export function SceneScreen() {
  const { state, dispatch } = useGame()
  const [completedSceneId, setCompletedSceneId] = useState<string | null>(null)

  const scene = state.currentSceneId ? state.story?.scenes[state.currentSceneId] ?? null : null
  const { blocked, distanceM } = useLocationGate(scene)

  const karaokeComplete = completedSceneId === state.currentSceneId
  const choicesLocked = !karaokeComplete || state.choiceLocked || blocked

  const handleKaraokeComplete = useCallback(() => {
    setCompletedSceneId(state.currentSceneId)
  }, [state.currentSceneId])

  const handleSelect = useCallback((option: Option) => {
    dispatch({ type: 'SELECT_OPTION', payload: option })
  }, [dispatch])

  useEffect(() => {
    if (!scene || choicesLocked) return
    const handleKey = (e: KeyboardEvent) => {
      const index = parseInt(e.key) - 1
      if (index >= 0 && index < scene.options.length) {
        handleSelect(scene.options[index])
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [choicesLocked, scene, handleSelect])

  if (!scene) return null

  const sceneParagraphs = resolveParagraphs(scene.scene, state.gameFields)
  const beforeStop = scene.before ? state.story?.stops[scene.before] ?? null : null
  const beforeShot = scene.before ? state.story?.streetview?.stops[scene.before] ?? null : null
  const locationShot = beforeShot ?? state.story?.streetview?.finale ?? null
  const locationLabel = beforeStop?.label ?? UI.scene.panelLocation

  if (blocked && beforeStop) {
    return (
      <GameLayout>
        <div className="w-full max-w-xl">
          <LocationGate stop={beforeStop} shot={beforeShot} distanceM={distanceM} />
        </div>
      </GameLayout>
    )
  }

  return (
    <SceneLayout
      story={
        <StoryPanel>
          <NarrativeKaraoke
            key={state.currentSceneId ?? undefined}
            paragraphs={sceneParagraphs}
            onComplete={handleKaraokeComplete}
          />
        </StoryPanel>
      }
      location={<LocationPanel shot={locationShot} label={locationLabel} />}
      choices={
        <ChoicesPanel
          options={scene.options}
          fields={state.gameFields}
          onSelect={handleSelect}
          locked={choicesLocked}
        />
      }
    />
  )
}
