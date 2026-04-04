<script setup lang="ts">
import { computed } from 'vue'
import type { EvaluatedGuess, GameConfig, GameStatus } from '../engine/types'
import TileRow from './TileRow.vue'

const emit = defineEmits<{ 'cursor-jump': [index: number] }>()

const props = defineProps<{
  guesses: EvaluatedGuess[]
  currentLetters: string[]
  cursorPosition: number
  config: GameConfig
  shakeRow: boolean
  revealRow: number
  bounceRow: number
  status: GameStatus
}>()

interface RowData {
  type: 'submitted' | 'active' | 'empty'
  letters?: import('../engine/types').EvaluatedLetter[]
  reveal?: boolean
  bounce?: boolean
  inputLetters?: string[]
  cursorIndex?: number
  shake?: boolean
}

const rows = computed<RowData[]>(() => {
  const result: RowData[] = []
  for (let i = 0; i < props.config.maxGuesses; i++) {
    if (i < props.guesses.length) {
      result.push({
        type: 'submitted',
        letters: props.guesses[i].letters,
        reveal: i === props.revealRow,
        bounce: i === props.bounceRow,
      })
    } else if (i === props.guesses.length && props.status === 'playing') {
      result.push({
        type: 'active',
        inputLetters: props.currentLetters,
        cursorIndex: props.cursorPosition,
        shake: props.shakeRow,
      })
    } else {
      result.push({ type: 'empty' })
    }
  }
  return result
})
</script>

<template>
  <div class="board">
    <TileRow
      v-for="(row, i) in rows"
      :key="`${i}-${row.type}`"
      :letters="row.letters"
      :input-letters="row.type === 'active' ? row.inputLetters : undefined"
      :cursor-index="row.type === 'active' ? row.cursorIndex : undefined"
      :word-length="config.wordLength"
      :reveal="row.reveal"
      :bounce="row.bounce"
      :shake="row.shake"
      :waiting="row.type === 'empty'"
      @cursor-jump="emit('cursor-jump', $event)"
    />
  </div>
</template>

<style scoped>
.board {
  display: flex;
  flex-direction: column;
  gap: var(--tile-gap);
  padding: 10px 0;
  flex-grow: 1;
  align-items: center;
  justify-content: center;
}
</style>
