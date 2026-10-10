import { useContext } from 'react'
import { GameContext } from './gameContext'
import type { GameContextValue } from './gameContext'

export function useGame(): GameContextValue {
  const ctx = useContext(GameContext)
  if (!ctx) throw new Error('useGame must be used inside GameProvider')
  return ctx
}
