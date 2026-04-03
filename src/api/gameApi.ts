import type {
  GameState,
  EvaluatedGuess,
  PlayerStats,
  GameConfig,
} from '../engine/types'
import { evaluateGuess } from '../engine/evaluate'
import {
  isValidWord,
  resolveAccented,
  getDailyWord,
  getDateKey,
} from '../data/words'
import * as storage from '../storage/storage'

export interface GameApi {
  getConfig(): GameConfig
  getTodayAnswer(): string
  getDateKey(): string
  validateWord(unaccentedInput: string): boolean
  submitGuess(unaccentedInput: string, answer: string): EvaluatedGuess
  resolveAccented(unaccentedInput: string): string
  loadGame(): GameState | null
  saveGame(state: GameState): void
  loadStats(): PlayerStats
  saveStats(stats: PlayerStats): void
}

export function createLocalApi(): GameApi {
  return {
    getConfig: () => ({ wordLength: 5, maxGuesses: 6 }),
    getTodayAnswer: () => getDailyWord(getDateKey()),
    getDateKey: () => getDateKey(),
    validateWord: isValidWord,
    submitGuess: (input, answer) => {
      const accentedGuess = resolveAccented(input)
      return evaluateGuess(accentedGuess, answer)
    },
    resolveAccented,
    loadGame: storage.loadGameState,
    saveGame: storage.saveGameState,
    loadStats: storage.loadStats,
    saveStats: storage.saveStats,
  }
}
