import type { GameState, PlayerStats, MultiGameState, GameMode } from '../engine/types'

const GAME_STATE_KEY = 'termo-pt-game'
const STATS_KEY = 'termo-pt-stats'
const ACTIVE_MODE_KEY = 'termo-pt-mode'

export function loadGameState(): GameState | null {
  const raw = localStorage.getItem(GAME_STATE_KEY)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function saveGameState(state: GameState): void {
  localStorage.setItem(GAME_STATE_KEY, JSON.stringify(state))
}

export function loadStats(): PlayerStats {
  const raw = localStorage.getItem(STATS_KEY)
  if (!raw) return defaultStats()
  try {
    return JSON.parse(raw)
  } catch {
    return defaultStats()
  }
}

export function saveStats(stats: PlayerStats): void {
  localStorage.setItem(STATS_KEY, JSON.stringify(stats))
}

function defaultStats(): PlayerStats {
  return {
    gamesPlayed: 0,
    gamesWon: 0,
    currentStreak: 0,
    maxStreak: 0,
    guessDistribution: [0, 0, 0, 0, 0, 0],
    lastPlayedDate: '',
  }
}

function defaultModeStats(maxGuesses: number): PlayerStats {
  return {
    gamesPlayed: 0,
    gamesWon: 0,
    currentStreak: 0,
    maxStreak: 0,
    guessDistribution: new Array(maxGuesses).fill(0),
    lastPlayedDate: '',
  }
}

export function loadMultiGameState(mode: string): MultiGameState | null {
  const raw = localStorage.getItem(`termo-pt-game-${mode}`)
  if (!raw) return null
  try {
    return JSON.parse(raw)
  } catch {
    return null
  }
}

export function saveMultiGameState(mode: string, state: MultiGameState): void {
  localStorage.setItem(`termo-pt-game-${mode}`, JSON.stringify(state))
}

export function loadModeStats(mode: string, maxGuesses: number): PlayerStats {
  const raw = localStorage.getItem(`termo-pt-stats-${mode}`)
  if (!raw) return defaultModeStats(maxGuesses)
  try {
    const stats = JSON.parse(raw) as PlayerStats
    if (stats.guessDistribution.length !== maxGuesses) {
      stats.guessDistribution = new Array(maxGuesses).fill(0)
    }
    return stats
  } catch {
    return defaultModeStats(maxGuesses)
  }
}

export function saveModeStats(mode: string, stats: PlayerStats): void {
  localStorage.setItem(`termo-pt-stats-${mode}`, JSON.stringify(stats))
}

export function loadActiveMode(): GameMode {
  const raw = localStorage.getItem(ACTIVE_MODE_KEY)
  if (raw === 'dueto' || raw === 'quarteto') return raw
  return 'termo'
}

export function saveActiveMode(mode: GameMode): void {
  localStorage.setItem(ACTIVE_MODE_KEY, mode)
}
