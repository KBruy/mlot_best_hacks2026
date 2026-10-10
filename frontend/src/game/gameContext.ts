import { createContext } from 'react'
import type { Dispatch } from 'react'
import type { GameState } from './types'
import type { GameAction } from './reducer'

export interface GameContextValue {
  state: GameState
  dispatch: Dispatch<GameAction>
}

export const GameContext = createContext<GameContextValue | null>(null)
