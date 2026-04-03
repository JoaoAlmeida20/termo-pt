import { ref, computed } from 'vue'
import type { EvaluatedGuess, GameStatus } from '../engine/types'
import type { GameApi } from '../api/gameApi'
import { aggregateKeyboardState } from '../engine/evaluate'

export function useGame(api: GameApi) {
  const config = api.getConfig()
  const wordLength = config.wordLength
  const dateKey = api.getDateKey()
  const answer = api.getTodayAnswer()

  const saved = api.loadGame()
  const isRestoredGame = saved?.dateKey === dateKey

  function inputStringToArray(s: string): string[] {
    const arr: string[] = Array(wordLength).fill('')
    for (let i = 0; i < Math.min(s.length, wordLength); i++) {
      arr[i] = s[i]
    }
    return arr
  }

  const currentLetters = ref<string[]>(
    isRestoredGame ? inputStringToArray(saved!.currentInput) : Array(wordLength).fill(''),
  )
  const cursorPosition = ref<number>(
    isRestoredGame ? Math.min(saved!.currentInput.length, wordLength - 1) : 0,
  )

  const currentInput = computed(() => currentLetters.value.join(''))

  const guesses = ref<EvaluatedGuess[]>(isRestoredGame ? saved!.guesses : [])
  const status = ref<GameStatus>(isRestoredGame ? saved!.status : 'playing')
  const shakeRow = ref(false)
  const revealRow = ref(-1)
  const bounceRow = ref(-1)

  const keyboardState = computed(() => aggregateKeyboardState(guesses.value))
  const isGameOver = computed(() => status.value !== 'playing')

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
    if (!api.validateWord(word)) {
      triggerShake()
      return false
    }

    const evaluated = api.submitGuess(word, answer)
    revealRow.value = guesses.value.length
    guesses.value.push(evaluated)
    currentLetters.value = Array(wordLength).fill('')
    cursorPosition.value = 0

    const isCorrect = evaluated.letters.every((l) => l.state === 'correct')
    if (isCorrect) {
      status.value = 'won'
      updateStats(true, guesses.value.length)
      const flipDuration = (wordLength - 1) * 300 + 600
      const winningRowIndex = guesses.value.length - 1
      setTimeout(() => {
        bounceRow.value = winningRowIndex
      }, flipDuration)
    } else if (guesses.value.length >= config.maxGuesses) {
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
    api.saveGame({
      dateKey,
      answer,
      guesses: guesses.value,
      currentInput: currentInput.value,
      status: status.value,
    })
  }

  function updateStats(won: boolean, numGuesses: number) {
    const stats = api.loadStats()
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
      console.log(`Updated stats: ${JSON.stringify(stats)}`)
    } else {
      stats.currentStreak = 0
    }
    stats.lastPlayedDate = dateKey
    api.saveStats(stats)
  }

  function resetGame() {
    guesses.value = []
    currentLetters.value = Array(wordLength).fill('')
    cursorPosition.value = 0
    status.value = 'playing'
    shakeRow.value = false
    revealRow.value = -1
    api.saveGame({
      dateKey,
      answer,
      guesses: [],
      currentInput: '',
      status: 'playing',
    })
  }

  function generateShareText(): string {
    const header = `Termo-PT ${dateKey} ${
      status.value === 'won' ? guesses.value.length : 'X'
    }/${config.maxGuesses}`
    const grid = guesses.value
      .map((g) =>
        g.letters
          .map((l) =>
            l.state === 'correct'
              ? '\u{1f7e9}'
              : l.state === 'present'
                ? '\u{1f7e8}'
                : '\u2b1b',
          )
          .join(''),
      )
      .join('\n')
    return `${header}\n\n${grid}`
  }

  return {
    guesses,
    currentLetters,
    currentInput,
    cursorPosition,
    status,
    keyboardState,
    shakeRow,
    revealRow,
    bounceRow,
    isGameOver,
    answer,
    config,
    addLetter,
    removeLetter,
    moveCursor,
    submitGuess,
    generateShareText,
    resetGame,
  }
}
