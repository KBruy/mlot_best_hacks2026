import { useState, useEffect, useCallback, useRef } from 'react'
import { PixelButton } from '@pxlkit/ui-kit'
import { useGame } from '../game/useGame'
import { UI } from '../strings'
import type { Variant } from '../game/types'

const WORD_MS = 60

// Jeden element audio na całą aplikację: po pierwszym odtworzeniu z gestu
// przeglądarki mobilne (iOS) pozwalają mu grać kolejne pliki bez nowego gestu.
const narrator = new Audio()

interface Timing {
  words: { text: string; start: number; end: number }[]
}

// Fallback, gdy obok MP3 nie ma .json (voice-service/NARRACJA.md): czas nagrania
// rozłożony na słowa proporcjonalnie do liter, z pauzami po interpunkcji.
function proportionalStarts(words: string[], duration: number): number[] {
  const pauses = words.map((word, i): number => {
    const prev = words[i - 1] ?? ''
    if (/^[—–]/.test(word)) return 0.5
    if (/[.?!…]$/.test(prev)) return 0.25
    if (/[,;:]$/.test(prev)) return 0.1
    return 0
  })
  const letters = words.map(w => w.replace(/[^\p{L}\p{N}]/gu, '').length || 1)
  const totalPause = pauses.reduce((a, b) => a + b, 0)
  const totalLetters = letters.reduce((a, b) => a + b, 0)
  const perLetter = Math.max(duration - totalPause, 0) / totalLetters
  let t = 0
  return words.map((_, i) => {
    t += pauses[i]
    const start = t
    t += letters[i] * perLetter
    return start
  })
}

async function loadStarts(url: string, words: string[], audio: HTMLAudioElement): Promise<number[]> {
  const fromJson = fetch(url.replace(/\.mp3$/, '.json'))
    .then(res => (res.ok ? (res.json() as Promise<Timing>) : null))
    .then(timing => (timing && timing.words.length === words.length ? timing.words.map(w => w.start) : null))
    .catch(() => null)
  const metadata = new Promise<void>(resolve =>
    audio.addEventListener('loadedmetadata', () => resolve(), { once: true }),
  )
  const [starts] = await Promise.all([fromJson, metadata])
  return starts ?? proportionalStarts(words, audio.duration)
}

interface Props {
  paragraphs: Variant[]
  onComplete?: () => void
  className?: string
}

export function NarrativeKaraoke({ paragraphs, onComplete, className = '' }: Props) {
  const { state, dispatch } = useGame()
  const [paraIndex, setParaIndex] = useState(0)
  const [wordCount, setWordCount] = useState(0)
  const [skipped, setSkipped] = useState(false)
  const [needsGesture, setNeedsGesture] = useState(false)
  const [audioFailedAt, setAudioFailedAt] = useState<number | null>(null)
  const calledRef = useRef(false)
  const wordCountRef = useRef(0)

  useEffect(() => {
    wordCountRef.current = wordCount
  }, [wordCount])

  const complete = skipped || paraIndex >= paragraphs.length
  const current = complete ? null : paragraphs[paraIndex]
  const text = current?.text ?? ''
  const wordTotal = text.split(' ').length
  const audioUrl = current?.audio_url && !state.muted && audioFailedAt !== paraIndex ? current.audio_url : null
  const hasAudio = paragraphs.some(p => p.audio_url)

  const advance = useCallback(() => {
    setParaIndex(i => i + 1)
    setWordCount(0)
    setNeedsGesture(false)
  }, [])

  useEffect(() => {
    if (complete && !calledRef.current) {
      calledRef.current = true
      onComplete?.()
    }
  }, [complete, onComplete])

  // Akapit bez nagrania (albo lektor wyciszony): stałe tempo.
  useEffect(() => {
    if (complete || audioUrl) return
    const timer = setTimeout(
      () => (wordCount < wordTotal ? setWordCount(wordCount + 1) : advance()),
      WORD_MS,
    )
    return () => clearTimeout(timer)
  }, [complete, audioUrl, wordCount, wordTotal, advance])

  // Akapit z nagraniem: słowo pojawia się, gdy lektor do niego dojdzie.
  useEffect(() => {
    if (complete || !audioUrl) return
    const words = text.split(' ')
    const listeners = new AbortController()
    let starts: number[] | null = null
    let frame = 0
    let cancelled = false

    const tick = () => {
      if (cancelled) return
      if (starts) {
        const t = narrator.currentTime
        setWordCount(starts.filter(s => t >= s).length)
      }
      frame = requestAnimationFrame(tick)
    }

    // Pętla klatek musi stanąć przed advance(), inaczej ostatni setWordCount
    // nadpisze zerowanie licznika i następny akapit zacznie się od środka.
    narrator.addEventListener('ended', () => {
      cancelled = true
      cancelAnimationFrame(frame)
      advance()
    }, { signal: listeners.signal })
    narrator.addEventListener('error', () => setAudioFailedAt(paraIndex), { signal: listeners.signal })
    narrator.src = audioUrl

    loadStarts(audioUrl, words, narrator).then(loaded => {
      if (cancelled) return
      starts = loaded
      // Wznowienie po włączeniu lektora w połowie akapitu.
      narrator.currentTime = loaded[wordCountRef.current] ?? 0
      narrator.play().catch((err: DOMException) => {
        if (cancelled) return
        if (err.name === 'NotAllowedError') setNeedsGesture(true)
        else setAudioFailedAt(paraIndex)
      })
    })
    frame = requestAnimationFrame(tick)

    return () => {
      cancelled = true
      listeners.abort()
      cancelAnimationFrame(frame)
      narrator.pause()
    }
  }, [complete, audioUrl, text, paraIndex, advance])

  const playFromGesture = useCallback(() => {
    narrator.play().then(() => setNeedsGesture(false)).catch(() => setAudioFailedAt(paraIndex))
  }, [paraIndex])

  const skip = useCallback(() => {
    if (!complete) setSkipped(true)
  }, [complete])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.code !== 'Space' || complete) return
      if (e.target instanceof HTMLElement && e.target.closest('button, a, input, textarea')) return
      e.preventDefault()
      skip()
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [skip, complete])

  return (
    <div className={className}>
      {hasAudio && (
        <div className="flex justify-end gap-2 mb-3">
          {needsGesture && audioUrl && (
            <PixelButton tone="gold" size="sm" onClick={playFromGesture}>
              ▶ {UI.narration.play}
            </PixelButton>
          )}
          <PixelButton
            tone="neutral"
            size="sm"
            aria-pressed={state.muted}
            aria-label={state.muted ? UI.narration.unmute : UI.narration.mute}
            title={state.muted ? UI.narration.unmute : UI.narration.mute}
            onClick={() => dispatch({ type: 'TOGGLE_MUTE' })}
          >
            {state.muted ? '🔇' : '🔊'}
          </PixelButton>
        </div>
      )}
      <div className="cursor-pointer select-none" onClick={skip} aria-live="polite">
        {paragraphs.map((p, i) => {
          const words = p.text.split(' ')
          const shown = complete || i < paraIndex ? words.length : i === paraIndex ? wordCount : 0
          return (
            <p key={i} className="narrative text-retro-muted mb-3">
              {words.slice(0, shown).join(' ')}
              {shown < words.length && (
                <span className="invisible">{(shown > 0 ? ' ' : '') + words.slice(shown).join(' ')}</span>
              )}
            </p>
          )
        })}
      </div>
    </div>
  )
}
