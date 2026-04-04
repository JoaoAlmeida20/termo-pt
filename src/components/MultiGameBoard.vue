<script setup lang="ts">
import type { EvaluatedGuess, GameStatus, MultiEvaluatedGuess, GameConfig } from '../engine/types'
import GameBoard from './GameBoard.vue'

const emit = defineEmits<{ 'cursor-jump': [index: number] }>()

const props = defineProps<{
  mode: 'dueto' | 'quarteto'
  guesses: MultiEvaluatedGuess[]
  wordStatuses: GameStatus[]
  overallStatus: GameStatus
  currentLetters: string[]
  cursorPosition: number
  config: GameConfig
  shakeRow: boolean
  revealRow: number
  bounceRows: number[]
}>()

function perWordGuesses(wordIndex: number): EvaluatedGuess[] {
  const allGuesses = props.guesses.map((mg) => mg.evaluations[wordIndex])
  const winIndex = allGuesses.findIndex((g) => g.letters.every((l) => l.state === 'correct'))
  return winIndex !== -1 ? allGuesses.slice(0, winIndex + 1) : allGuesses
}

function boardStatus(wordIndex: number): GameStatus {
  if (props.overallStatus === 'lost') return 'lost'
  return props.wordStatuses[wordIndex]
}
</script>

<template>
  <div class="multi-board" :class="`multi-board--${mode}`">
    <div
      v-for="i in (mode === 'dueto' ? 2 : 4)"
      :key="i"
      class="board-cell"
    >
      <GameBoard
        :guesses="perWordGuesses(i - 1)"
        :current-letters="currentLetters"
        :cursor-position="cursorPosition"
        :config="config"
        :shake-row="shakeRow"
        :reveal-row="revealRow"
        :bounce-row="bounceRows[i - 1]"
        :status="boardStatus(i - 1)"
        @cursor-jump="emit('cursor-jump', $event)"
      />
    </div>
  </div>
</template>

<style scoped>
.multi-board {
  flex: 1 1 0;
  display: grid;
  width: 100%;
  padding: 4px 8px;
  gap: 8px;
}

.multi-board--dueto {
  grid-template-columns: 1fr 1fr;
  --tile-size: min(62px, calc((50vw - 40px) / 5));
}

.multi-board--quarteto {
  grid-template-columns: 1fr 1fr;
  --tile-size: min(52px, calc((50vw - 40px) / 5), calc((85dvh - 191px) / 18));
}

@media (min-width: 600px) {
  .multi-board--quarteto {
    grid-template-columns: repeat(4, 1fr);
    --tile-size: min(52px, calc((25vw - 30px) / 5), calc((85dvh - 131px) / 9));
  }
}

.board-cell {
  display: flex;
  flex-direction: column;
  min-height: 0;
}
</style>
