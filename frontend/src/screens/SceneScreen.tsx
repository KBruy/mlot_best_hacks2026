import { useState, useEffect, useCallback } from 'react'
import { useGame } from '../game/useGame'
import { useLocationGate } from '../map/useLocationGate'
import { resolveParagraphs } from '../game/textUtils'
import { bearingDeg } from '../map/distance'
import { SceneLayout } from '../components/SceneLayout'
import { StoryPanel } from '../components/StoryPanel'
import { LocationPanel } from '../components/LocationPanel'
import { ChoicesPanel } from '../components/ChoicesPanel'
import { LocationGate } from '../components/LocationGate'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { UI } from '../strings'
import type { Option, StreetViewShot } from '../game/types'

export function SceneScreen() {
  const { state, dispatch } = useGame()
  const [completedSceneId, setCompletedSceneId] = useState<string | null>(null)

  const scene = state.currentSceneId ? state.story?.scenes[state.currentSceneId] ?? null : null
  const { blocked, distanceM } = useLocationGate(scene)

  const anchors = state.story?.streetview?.anchors
  const beforeStop = scene?.before ? state.story?.stops[scene.before] ?? null : null
  const beforeShot = scene?.before ? state.story?.streetview?.stops[scene.before] ?? null : null

  const isDemoWalk = state.demoMode && !!scene?.before && !!anchors?.length

  // Demo walk: track { sceneId, frame } — frame advances via interval callback (async)
  const [walk, setWalk] = useState<{ sceneId: string; frame: number } | null>(null)

  useEffect(() => {
    if (!isDemoWalk) return
    const id = setInterval(() => {
      setWalk(prev => ({
        sceneId: state.currentSceneId ?? '',
        frame: prev?.sceneId === state.currentSceneId ? prev.frame + 1 : 1,
      }))
    }, 1000)
    return () => clearInterval(id)
  }, [state.currentSceneId, isDemoWalk])

  const walkFrame = walk?.sceneId === state.currentSceneId ? walk.frame : 0
  const walkDone = !isDemoWalk || walkFrame >= (anchors?.length ?? 0)

  // Street View shot for the location panel
  const walkShot: StreetViewShot | null = (() => {
    if (!isDemoWalk) return beforeShot ?? state.story?.streetview?.finale ?? null
    if (!anchors || walkFrame >= anchors.length) return beforeShot ?? null
    const [ancLat, ancLon] = anchors[walkFrame]
    return {
      lat: ancLat,
      lon: ancLon,
      heading: beforeStop
        ? bearingDeg(ancLat, ancLon, beforeStop.lat, beforeStop.lon)
        : 0,
      pitch: 0,
    }
  })()

  const locationShot = walkShot ?? state.story?.streetview?.finale ?? null
  const locationLabel = beforeStop?.label ?? UI.scene.panelLocation

  const karaokeComplete = completedSceneId === state.currentSceneId
  const choicesLocked = !karaokeComplete || state.choiceLocked || blocked || !walkDone

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

  // Live mode: blocked by GPS
  if (blocked && beforeStop) {
    return (
      <GameLayout>
        <div className="w-full max-w-xl">
          <LocationGate
            stop={beforeStop}
            shot={beforeShot}
            anchors={anchors}
            distanceM={distanceM}
          />
        </div>
      </GameLayout>
    )
  }

  const sceneText = resolveParagraphs(scene.scene, state.gameFields).join('\n\n')

  return (
    <SceneLayout
      story={
        <StoryPanel>
          {walkDone && (
            <NarrativeKaraoke
              key={state.currentSceneId ?? undefined}
              text={sceneText}
              onComplete={handleKaraokeComplete}
            />
          )}
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
