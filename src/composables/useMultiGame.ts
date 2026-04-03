import { ref, computed } from 'vue'
import type { EvaluatedGuess, GameStatus, MultiEvaluatedGuess } from '../engine/types'
import { evaluateGuess, getMultiKeyboardStates } from '../engine/evaluate'
import { isValidWord, resolveAccented, getDailyWords, getDateKey } from '../data/words'
import * as storage from '../storage/storage'

export function useMultiGame(mode: 'dueto' | 'quarteto') {
  const wordCount = mode === 'dueto' ? 2 : 4
  const maxGuesses = mode === 'dueto' ? 7 : 9
  const wordLength = 5
  const config = { wordLength, maxGuesses }

  const dateKey = getDateKey()
  const answers = getDailyWords(dateKey, wordCount, mode)

  const saved = storage.loadMultiGameState(mode)
  const isRestoredGame = saved?.dateKey === dateKey && saved?.mode === mode

  function inputStringToArray(s: string): string[] {
    const arr: string[] = Array(wordLength).fill('')
    for (let i = 0; i < Math.min(s.length, wordLength); i++) {
      arr[i] = s[i]
    }
    return arr
  }

  const guesses = ref<MultiEvaluatedGuess[]>(isRestoredGame ? saved!.guesses : [])
  const wordStatuses = ref<GameStatus[]>(
    isRestoredGame ? saved!.wordStatuses : (Array(wordCount).fill('playing') as GameStatus[]),
  )
  const status = ref<GameStatus>(isRestoredGame ? saved!.status : 'playing')
  const currentLetters = ref<string[]>(
    isRestoredGame ? inputStringToArray(saved!.currentInput) : Array(wordLength).fill(''),
  )
  const cursorPosition = ref<number>(
    isRestoredGame ? Math.min(saved!.currentInput.length, wordLength - 1) : 0,
  )

  const shakeRow = ref(false)
  const revealRow = ref(-1)
  const bounceRows = ref<number[]>(Array(wordCount).fill(-1))

  const currentInput = computed(() => currentLetters.value.join(''))
  const isGameOver = computed(() => status.value !== 'playing')

  const keyboardState = computed(() => getMultiKeyboardStates(guesses.value, wordCount))

  function addLetter(letter: string) {
    if (isGameOver.value) return
    currentLetters.value[cursorPosition.value] = letter.toLowerCase()
    let currentCursorPosition = cursorPosition.value
    let nextCursorPosition = (currentCursorPosition + 1) % wordLength
    while (nextCursorPosition !== currentCursorPosition) {
      if (currentLetters.value[nextCursorPosition] === '') {
        break
      }
      nextCursorPosition = (nextCursorPosition + 1) % wordLength
    }
    cursorPosition.value = nextCursorPosition
  }

  function removeLetter() {
    if (isGameOver.value) return
    if (currentLetters.value[cursorPosition.value] !== '') {
      currentLetters.value[cursorPosition.value] = ''
    } else if (cursorPosition.value > 0) {
      cursorPosition.value--
      currentLetters.value[cursorPosition.value] = ''
    }
  }

  function moveCursor(delta: number) {
    if (isGameOver.value) return
    cursorPosition.value = Math.max(0, Math.min(wordLength - 1, cursorPosition.value + delta))
  }

  function submitGuess(): boolean {
    if (isGameOver.value) return false
    if (currentLetters.value.some((l) => l === '')) {
      triggerShake()
      return false
    }
    const word = currentLetters.value.join('')
    if (!isValidWord(word)) {
      triggerShake()
      return false
    }

    const accentedGuess = resolveAccented(word)
    const evaluations: EvaluatedGuess[] = answers.map((answer) =>
      evaluateGuess(accentedGuess, answer),
    )

    const guessIndex = guesses.value.length
    revealRow.value = guessIndex
    guesses.value.push({ evaluations })
    currentLetters.value = Array(wordLength).fill('')
    cursorPosition.value = 0

    const flipDuration = (wordLength - 1) * 300 + 600

    // Check per-word correctness
    for (let i = 0; i < wordCount; i++) {
      if (wordStatuses.value[i] === 'won') continue
      const isCorrect = evaluations[i].letters.every((l) => l.state === 'correct')
      if (isCorrect) {
        wordStatuses.value[i] = 'won'
        const wi = i
        const gi = guessIndex
        setTimeout(() => {
          const next = [...bounceRows.value]
          next[wi] = gi
          bounceRows.value = next
        }, flipDuration)
      }
    }

    const allWon = wordStatuses.value.every((s) => s === 'won')
    if (allWon) {
      status.value = 'won'
      updateStats(true, guesses.value.length)
    } else if (guesses.value.length >= maxGuesses) {
      status.value = 'lost'
      updateStats(false, guesses.value.length)
    }

    persistState()
    return true
  }

  function triggerShake() {
    shakeRow.value = true
    setTimeout(() => {
      shakeRow.value = false
    }, 600)
  }

  function persistState() {
    storage.saveMultiGameState(mode, {
      dateKey,
      mode,
      answers,
      guesses: guesses.value,
      currentInput: currentInput.value,
      wordStatuses: wordStatuses.value,
      status: status.value,
    })
  }

  function updateStats(won: boolean, numGuesses: number) {
    const stats = storage.loadModeStats(mode, maxGuesses)
    stats.gamesPlayed++
    if (won) {
      stats.gamesWon++
      stats.guessDistribution[numGuesses - 1]++
      const yesterday = new Date()
      yesterday.setDate(yesterday.getDate() - 1)
      const yesterdayKey = yesterday.toISOString().slice(0, 10)
      stats.currentStreak =
        stats.lastPlayedDate === yesterdayKey ? stats.currentStreak + 1 : 1
      stats.maxStreak = Math.max(stats.maxStreak, stats.currentStreak)
    } else {
      stats.currentStreak = 0
    }
    stats.lastPlayedDate = dateKey
    storage.saveModeStats(mode, stats)
  }

  function resetGame() {
    guesses.value = []
    currentLetters.value = Array(wordLength).fill('')
    cursorPosition.value = 0
    status.value = 'playing'
    wordStatuses.value = Array(wordCount).fill('playing') as GameStatus[]
    shakeRow.value = false
    revealRow.value = -1
    bounceRows.value = Array(wordCount).fill(-1)
    storage.saveMultiGameState(mode, {
      dateKey,
      mode,
      answers,
      guesses: [],
      currentInput: '',
      wordStatuses: Array(wordCount).fill('playing') as GameStatus[],
      status: 'playing',
    })
  }

  function generateShareText(): string {
    const modeName = mode === 'dueto' ? 'Dueto' : 'Quarteto'
    const header = `Termo-PT ${modeName} ${dateKey} ${
      status.value === 'won' ? guesses.value.length : 'X'
    }/${maxGuesses}`
    const grid = guesses.value
      .map((mg) =>
        mg.evaluations
          .map((ev) =>
            ev.letters
              .map((l) =>
                l.state === 'correct'
                  ? '\u{1f7e9}'
                  : l.state === 'present'
                    ? '\u{1f7e8}'
                    : '\u2b1b',
              )
              .join(''),
          )
          .join(' '),
      )
      .join('\n')
    return `${header}\n\n${grid}`
  }

  return {
    guesses,
    wordStatuses,
    status,
    currentLetters,
    currentInput,
    cursorPosition,
    keyboardState,
    shakeRow,
    revealRow,
    bounceRows,
    isGameOver,
    answers,
    config,
    addLetter,
    removeLetter,
    moveCursor,
    submitGuess,
    generateShareText,
    resetGame,
  }
}
