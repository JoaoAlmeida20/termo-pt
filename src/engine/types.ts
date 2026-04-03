export type LetterState = 'correct' | 'present' | 'absent'

export interface EvaluatedLetter {
  letter: string
  unaccented: string
  state: LetterState
}

export interface EvaluatedGuess {
  letters: EvaluatedLetter[]
}

export type GameStatus = 'playing' | 'won' | 'lost'

export interface GameState {
  dateKey: string
  answer: string
  guesses: EvaluatedGuess[]
  currentInput: string
  status: GameStatus
}

export interface PlayerStats {
  gamesPlayed: number
  gamesWon: number
  currentStreak: number
  maxStreak: number
  guessDistribution: number[]
  lastPlayedDate: string
}

export interface GameConfig {
  wordLength: number
  maxGuesses: number
}

export type GameMode = 'termo' | 'dueto' | 'quarteto'

export interface MultiEvaluatedGuess {
  evaluations: EvaluatedGuess[]  // one EvaluatedGuess per target word
}

export interface MultiGameState {
  dateKey: string
  mode: GameMode
  answers: string[]
  guesses: MultiEvaluatedGuess[]
  currentInput: string
  wordStatuses: GameStatus[]
  status: GameStatus
}
