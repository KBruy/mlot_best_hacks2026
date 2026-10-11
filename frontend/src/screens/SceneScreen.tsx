import { useState, useEffect, useCallback, useMemo } from 'react'
import { useGame } from '../game/useGame'
import { useLocationGate } from '../map/useLocationGate'
import { resolveParagraphs } from '../game/textUtils'
import { bearingDeg, haversineDistance } from '../map/distance'
import { SceneLayout } from '../components/SceneLayout'
import { StoryPanel } from '../components/StoryPanel'
import { LocationPanel } from '../components/LocationPanel'
import { ChoicesPanel } from '../components/ChoicesPanel'
import { LocationGate } from '../components/LocationGate'
import { GameLayout } from '../components/GameLayout'
import { NarrativeKaraoke } from '../components/NarrativeKaraoke'
import { UI } from '../strings'
import type { Option, StreetViewShot } from '../game/types'

function nearestAnchorIdx(anchors: [number, number][], lat: number, lon: number): number {
  let best = 0
  let bestDist = Infinity
  for (let i = 0; i < anchors.length; i++) {
    const d = haversineDistance(lat, lon, anchors[i][0], anchors[i][1])
    if (d < bestDist) { bestDist = d; best = i }
  }
  return best
}

export function SceneScreen() {
  const { state, dispatch } = useGame()
  const [completedSceneId, setCompletedSceneId] = useState<string | null>(null)

  const scene = state.currentSceneId ? state.story?.scenes[state.currentSceneId] ?? null : null
  const { blocked, distanceM } = useLocationGate(scene)

  const allAnchors = state.story?.streetview?.anchors ?? null
  const beforeStop = scene?.before ? state.story?.stops[scene.before] ?? null : null
  const beforeShot = scene?.before ? state.story?.streetview?.stops[scene.before] ?? null : null

  const isDemoWalk = state.demoMode && !!scene?.before && !!allAnchors?.length

  // Segment anchors: only the portion of the route relevant to the current stop
  const segmentAnchors = useMemo<[number, number][] | null>(() => {
    if (!isDemoWalk || !allAnchors || !beforeStop) return null
    const prevStop = state.lastStop ? state.story?.stops[state.lastStop] : null
    const endIdx = nearestAnchorIdx(allAnchors, beforeStop.lat, beforeStop.lon)
    // First walk (no lastStop): always start from anchor 0 — demo_start sits at the
    // destination, so nearest-anchor logic would collapse the segment to a single frame.
    const startIdx = prevStop
      ? nearestAnchorIdx(allAnchors, prevStop.lat, prevStop.lon)
      : 0
    return allAnchors.slice(startIdx, endIdx + 1)
  }, [isDemoWalk, allAnchors, beforeStop, state.lastStop, state.story])

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
  const walkDone = !isDemoWalk || walkFrame >= (segmentAnchors?.length ?? 0)

  // Street View shot during demo walk — heading toward next anchor, last anchor toward stop
  const walkShot: StreetViewShot | null = (() => {
    if (!isDemoWalk || !segmentAnchors) return null
    if (walkFrame >= segmentAnchors.length) return beforeShot ?? null
    const [ancLat, ancLon] = segmentAnchors[walkFrame]
    let heading = 0
    if (walkFrame + 1 < segmentAnchors.length) {
      heading = bearingDeg(ancLat, ancLon, segmentAnchors[walkFrame + 1][0], segmentAnchors[walkFrame + 1][1])
    } else if (beforeStop) {
      heading = bearingDeg(ancLat, ancLon, beforeStop.lat, beforeStop.lon)
    }
    return { lat: ancLat, lon: ancLon, heading, pitch: 0 }
  })()

  // Static shot for non-walk scenes: last stop's fixed view, or nearest anchor to demo_start
  const staticShot: StreetViewShot | null = (() => {
    if (!state.story) return null
    if (state.lastStop) {
      return state.story.streetview?.stops[state.lastStop] ?? null
    }
    if (!allAnchors?.length) return null
    const pos: [number, number] | null = state.demoMode && state.story.demo_start
      ? [state.story.demo_start[0], state.story.demo_start[1]]
      : state.gpsPosition ? [state.gpsPosition.lat, state.gpsPosition.lon] : null
    if (!pos) return null
    const idx = nearestAnchorIdx(allAnchors, pos[0], pos[1])
    const [ancLat, ancLon] = allAnchors[idx]
    const center = state.story.location.center
    return { lat: ancLat, lon: ancLon, heading: bearingDeg(ancLat, ancLon, center[0], center[1]), pitch: 0 }
  })()

  const locationShot: StreetViewShot | null = isDemoWalk ? walkShot : staticShot
  const locationLabel = beforeStop?.label ?? UI.scene.panelLocation

  const karaokeComplete = completedSceneId === state.currentSceneId
  const choicesLocked = !karaokeComplete || state.choiceLocked || blocked || !walkDone

  const handleKaraokeComplete = useCallback(() => {
    setCompletedSceneId(state.currentSceneId)
  }, [state.currentSceneId])

  const handleSelect = useCallback((option: Option) => {
    dispatch({ type: 'SELECT_OPTION', payload: option })
  }, [dispatch])

  const skipWalk = useCallback(() => {
    if (!isDemoWalk || walkDone) return
    setWalk({ sceneId: state.currentSceneId ?? '', frame: segmentAnchors?.length ?? 0 })
  }, [isDemoWalk, walkDone, state.currentSceneId, segmentAnchors?.length])

  useEffect(() => {
    if (!isDemoWalk || walkDone) return
    const handleKey = (e: KeyboardEvent) => {
      if (e.code === 'Space') { e.preventDefault(); skipWalk() }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [isDemoWalk, walkDone, skipWalk])

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

  if (blocked && beforeStop) {
    return (
      <GameLayout>
        <div className="w-full max-w-xl">
          <LocationGate
            stop={beforeStop}
            shot={beforeShot}
            anchors={allAnchors}
            distanceM={distanceM}
          />
        </div>
      </GameLayout>
    )
  }

  const sceneParagraphs = resolveParagraphs(scene.scene, state.gameFields)

  return (
    <SceneLayout
      story={
        <StoryPanel>
          {walkDone ? (
            <NarrativeKaraoke
              key={state.currentSceneId ?? undefined}
              paragraphs={sceneParagraphs}
              onComplete={handleKaraokeComplete}
            />
          ) : (
            <p className="narrative text-retro-muted opacity-60 italic">
              Podróż do: {beforeStop?.label ?? locationLabel}…
            </p>
          )}
        </StoryPanel>
      }
      location={<LocationPanel shot={locationShot} label={locationLabel} onBack={() => dispatch({ type: 'RESTART' })} />}
      choices={
        walkDone ? (
          <ChoicesPanel
            options={scene.options}
            fields={state.gameFields}
            onSelect={handleSelect}
            locked={choicesLocked}
          />
        ) : (
          <div className="w-full h-full border-t-2 border-retro-border-strong bg-retro-surface" />
        )
      }
    />
  )
}
