import { useState, useEffect, useCallback, useRef } from 'react'

interface Props {
  text: string
  onComplete: () => void
  className?: string
}

export function NarrativeKaraoke({ text, onComplete, className = '' }: Props) {
  const words = text.split(' ')
  const [visibleCount, setVisibleCount] = useState(0)
  const calledRef = useRef(false)

  const complete = visibleCount >= words.length

  useEffect(() => {
    if (complete) {
      if (!calledRef.current) {
        calledRef.current = true
        onComplete()
      }
      return
    }
    const timer = setTimeout(() => setVisibleCount(n => n + 1), 60)
    return () => clearTimeout(timer)
  }, [visibleCount, complete, onComplete])

  const skip = useCallback(() => {
    if (!complete) setVisibleCount(words.length)
  }, [complete, words.length])

  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => {
      if (e.code === 'Space' && !complete) {
        e.preventDefault()
        skip()
      }
    }
    window.addEventListener('keydown', handleKey)
    return () => window.removeEventListener('keydown', handleKey)
  }, [skip, complete])

  return (
    <p
      className={`narrative text-retro-muted cursor-pointer select-none ${className}`}
      onClick={skip}
      aria-live="polite"
    >
      {words.slice(0, visibleCount).join(' ')}
      {!complete && (
        <span className="invisible">{' ' + words.slice(visibleCount).join(' ')}</span>
      )}
    </p>
  )
}
