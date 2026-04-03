<script setup lang="ts">
import { ref, computed, watch, watchEffect } from 'vue'
import confetti from 'canvas-confetti'
import type { LetterState, GameMode } from './engine/types'
import { createLocalApi } from './api/gameApi'
import { useGame } from './composables/useGame'
import { useMultiGame } from './composables/useMultiGame'
import { useKeyboard } from './composables/useKeyboard'
import { useTheme } from './composables/useTheme'
import { loadActiveMode, saveActiveMode, loadStats, loadModeStats } from './storage/storage'
import AppHeader from './components/AppHeader.vue'
import GameBoard from './components/GameBoard.vue'
import MultiGameBoard from './components/MultiGameBoard.vue'
import Keyboard from './components/Keyboard.vue'
import StatsModal from './components/StatsModal.vue'
import HelpModal from './components/HelpModal.vue'
import InfoModal from './components/InfoModal.vue'

const api = createLocalApi()
const theme = useTheme()

// Always instantiate all three game composables (composables cannot be conditional)
const termoGame = useGame(api)
const duetGame = useMultiGame('dueto')
const quartetoGame = useMultiGame('quarteto')

const activeMode = ref<GameMode>(loadActiveMode())
const showStats = ref(false)
const showHelp = ref(false)
const showInfo = ref(false)

// Set data-mode attribute on #app for CSS max-width overrides
watchEffect(() => {
  const appEl = document.getElementById('app')
  if (appEl) appEl.dataset.mode = activeMode.value
})

// Active game handlers — delegate keyboard to the right game
const activeHandlers = computed(() => {
  if (activeMode.value === 'dueto') return duetGame
  if (activeMode.value === 'quarteto') return quartetoGame
  return termoGame
})

useKeyboard({
  onLetter: (l) => activeHandlers.value.addLetter(l),
  onEnter: () => activeHandlers.value.submitGuess(),
  onBackspace: () => activeHandlers.value.removeLetter(),
  onArrowLeft: () => activeHandlers.value.moveCursor(-1),
  onArrowRight: () => activeHandlers.value.moveCursor(1),
})

// Convert termo's Map<string, LetterState> to Map<string, LetterState[]>
const termoKeyStates = computed<Map<string, LetterState[]>>(() => {
  const result = new Map<string, LetterState[]>()
  for (const [k, v] of termoGame.keyboardState.value) {
    result.set(k, [v])
  }
  return result
})

const currentKeyStates = computed<Map<string, LetterState[]>>(() => {
  if (activeMode.value === 'dueto') return duetGame.keyboardState.value
  if (activeMode.value === 'quarteto') return quartetoGame.keyboardState.value
  return termoKeyStates.value
})

// Stats data for the modal (mode-specific)
function loadCurrentStats() {
  if (activeMode.value === 'dueto') return loadModeStats('dueto', 7)
  if (activeMode.value === 'quarteto') return loadModeStats('quarteto', 9)
  return loadStats()
}
const currentStats = ref(loadCurrentStats())

function refreshStats() {
  currentStats.value = loadCurrentStats()
}

const currentAnswers = computed<string[]>(() => {
  if (activeMode.value === 'dueto') return duetGame.answers
  if (activeMode.value === 'quarteto') return quartetoGame.answers
  return [termoGame.answer]
})

const currentShareText = computed(() => {
  if (activeMode.value === 'dueto') return duetGame.generateShareText()
  if (activeMode.value === 'quarteto') return quartetoGame.generateShareText()
  return termoGame.generateShareText()
})

const currentGameStatus = computed(() => {
  if (activeMode.value === 'dueto') return duetGame.status.value
  if (activeMode.value === 'quarteto') return quartetoGame.status.value
  return termoGame.status.value
})

const currentGuessCount = computed(() => {
  if (activeMode.value === 'dueto') return duetGame.guesses.value.length
  if (activeMode.value === 'quarteto') return quartetoGame.guesses.value.length
  return termoGame.guesses.value.length
})

// Confetti + stats modal for Termo
watch(termoGame.bounceRow, (row) => {
  if (row >= 0 && activeMode.value === 'termo') {
    confetti({
      particleCount: 150,
      spread: 90,
      origin: { y: 1.0 },
      angle: 90,
      startVelocity: 60,
    })
  }
})

watch(termoGame.status, (s) => {
  if (s === 'playing' || activeMode.value !== 'termo') return
  const delay = s === 'won' ? 3800 : 1800
  setTimeout(() => {
    refreshStats()
    showStats.value = true
  }, delay)
})

// Confetti + stats modal for multi-game modes
function handleMultiGameEnd(mode: 'dueto' | 'quarteto', s: string) {
  if (activeMode.value !== mode) return
  if (s === 'won') {
    const flipDuration = (5 - 1) * 300 + 600 + 200
    setTimeout(() => {
      confetti({
        particleCount: 150,
        spread: 90,
        origin: { y: 1.0 },
        angle: 90,
        startVelocity: 60,
      })
    }, flipDuration)
    setTimeout(() => {
      refreshStats()
      showStats.value = true
    }, 3800)
  } else if (s === 'lost') {
    setTimeout(() => {
      refreshStats()
      showStats.value = true
    }, 1800)
  }
}

watch(duetGame.status, (s) => handleMultiGameEnd('dueto', s))
watch(quartetoGame.status, (s) => handleMultiGameEnd('quarteto', s))

function changeMode(mode: GameMode) {
  showStats.value = false
  saveActiveMode(mode)
  activeMode.value = mode
}

function clearGame() {
  activeHandlers.value.resetGame()
}
</script>

<template>
  <AppHeader
    :is-dark="theme.isDark.value"
    :current-mode="activeMode"
    @toggle-theme="theme.toggle"
    @show-help="showHelp = true"
    @show-info="showInfo = true"
    @show-stats="refreshStats(); showStats = true"
    @clear-game="clearGame"
    @change-mode="changeMode"
  />

  <GameBoard
    v-if="activeMode === 'termo'"
    :guesses="termoGame.guesses.value"
    :current-letters="termoGame.currentLetters.value"
    :cursor-position="termoGame.cursorPosition.value"
    :config="termoGame.config"
    :shake-row="termoGame.shakeRow.value"
    :reveal-row="termoGame.revealRow.value"
    :bounce-row="termoGame.bounceRow.value"
    :status="termoGame.status.value"
  />

  <MultiGameBoard
    v-else
    :mode="activeMode"
    :guesses="activeMode === 'dueto' ? duetGame.guesses.value : quartetoGame.guesses.value"
    :word-statuses="activeMode === 'dueto' ? duetGame.wordStatuses.value : quartetoGame.wordStatuses.value"
    :overall-status="activeMode === 'dueto' ? duetGame.status.value : quartetoGame.status.value"
    :current-letters="activeMode === 'dueto' ? duetGame.currentLetters.value : quartetoGame.currentLetters.value"
    :cursor-position="activeMode === 'dueto' ? duetGame.cursorPosition.value : quartetoGame.cursorPosition.value"
    :config="activeMode === 'dueto' ? duetGame.config : quartetoGame.config"
    :shake-row="activeMode === 'dueto' ? duetGame.shakeRow.value : quartetoGame.shakeRow.value"
    :reveal-row="activeMode === 'dueto' ? duetGame.revealRow.value : quartetoGame.revealRow.value"
    :bounce-rows="activeMode === 'dueto' ? duetGame.bounceRows.value : quartetoGame.bounceRows.value"
  />

  <Keyboard
    :keyboard-state="currentKeyStates"
    @key="activeHandlers.addLetter"
    @enter="activeHandlers.submitGuess"
    @backspace="activeHandlers.removeLetter"
  />

  <StatsModal
    v-if="showStats"
    :stats="currentStats"
    :game-status="currentGameStatus"
    :guess-count="currentGuessCount"
    :share-text="currentShareText"
    :answers="currentAnswers"
    @close="showStats = false"
  />
  <HelpModal v-if="showHelp" @close="showHelp = false" />
  <InfoModal v-if="showInfo" @close="showInfo = false" />
</template>
