import type { EvaluatedGuess, EvaluatedLetter, LetterState, MultiEvaluatedGuess } from './types'
import { stripAccents } from './accents'

export function evaluateGuess(
  guessAccented: string,
  answerAccented: string,
): EvaluatedGuess {
  const guess = stripAccents(guessAccented)
  const answer = stripAccents(answerAccented)
  const length = guess.length

  const states: LetterState[] = new Array(length).fill('absent')
  const consumed: boolean[] = new Array(length).fill(false)

  // Pass 1: exact matches
  for (let i = 0; i < length; i++) {
    if (guess[i] === answer[i]) {
      states[i] = 'correct'
      consumed[i] = true
    }
  }

  // Pass 2: present (wrong position)
  for (let i = 0; i < length; i++) {
    if (states[i] === 'correct') continue
    for (let j = 0; j < length; j++) {
      if (!consumed[j] && guess[i] === answer[j]) {
        states[i] = 'present'
        consumed[j] = true
        break
      }
    }
  }

  const letters: EvaluatedLetter[] = []
  for (let i = 0; i < length; i++) {
    letters.push({
      letter: guessAccented[i],
      unaccented: guess[i],
      state: states[i],
    })
  }

  return { letters }
}

// Returns per-word LetterState for each letter that has appeared in guesses.
// Index 0 = word 0, index 1 = word 1, etc.
export function getMultiKeyboardStates(
  guesses: MultiEvaluatedGuess[],
  wordCount: number,
): Map<string, LetterState[]> {
  const priority: Record<LetterState, number> = { correct: 2, present: 1, absent: 0 }
  const map = new Map<string, LetterState[]>()

  for (const multiGuess of guesses) {
    if (multiGuess.evaluations.length === 0) continue
    const letterCount = multiGuess.evaluations[0].letters.length
    for (let li = 0; li < letterCount; li++) {
      const unaccented = multiGuess.evaluations[0].letters[li].unaccented
      if (!map.has(unaccented)) {
        map.set(unaccented, new Array(wordCount).fill('absent') as LetterState[])
      }
      const states = map.get(unaccented)!
      for (let wi = 0; wi < wordCount; wi++) {
        const ev = multiGuess.evaluations[wi]
        if (!ev) continue
        const state = ev.letters[li].state
        if (priority[state] > priority[states[wi]]) {
          states[wi] = state
        }
      }
    }
  }

  return map
}

export function aggregateKeyboardState(
  guesses: EvaluatedGuess[],
): Map<string, LetterState> {
  const priority: Record<LetterState, number> = {
    correct: 2,
    present: 1,
    absent: 0,
  }
  const map = new Map<string, LetterState>()
  for (const guess of guesses) {
    for (const { unaccented, state } of guess.letters) {
      const current = map.get(unaccented)
      if (!current || priority[state] > priority[current]) {
        map.set(unaccented, state)
      }
    }
  }
  return map
}
