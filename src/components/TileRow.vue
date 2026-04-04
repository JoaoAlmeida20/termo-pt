<script setup lang="ts">
import type { EvaluatedLetter } from '../engine/types'
import Tile from './Tile.vue'

const emit = defineEmits<{ 'cursor-jump': [index: number] }>()

const props = defineProps<{
  letters?: EvaluatedLetter[]
  inputLetters?: string[]
  cursorIndex?: number
  wordLength: number
  shake?: boolean
  reveal?: boolean
  bounce?: boolean
  waiting?: boolean
}>()

function handleTileClick(index: number) {
  if (props.inputLetters !== undefined) {
    emit('cursor-jump', index)
  }
}

function getTileProps(index: number) {
  if (props.letters) {
    return {
      letter: props.letters[index].letter,
      state: props.letters[index].state,
      reveal: props.reveal,
      delay: index * 300,
      bounce: props.bounce,
      bounceDelay: index * 100,
      isCursor: false,
    }
  }
  if (props.inputLetters !== undefined) {
    const char = props.inputLetters[index] ?? ''
    return {
      letter: char,
      state: char ? ('input' as const) : ('empty' as const),
      reveal: false,
      delay: 0,
      bounce: false,
      bounceDelay: 0,
      isCursor: index === props.cursorIndex,
    }
  }
  return {
    letter: '',
    state: 'empty' as const,
    reveal: false,
    delay: 0,
    bounce: false,
    bounceDelay: 0,
    isCursor: false,
    waiting: props.waiting,
  }
}
</script>

<template>
  <div class="tile-row" :class="{ shake }">
    <Tile v-for="i in wordLength" :key="i - 1" v-bind="getTileProps(i - 1)" @click="handleTileClick(i - 1)" />
  </div>
</template>

<style scoped>
.tile-row {
  display: flex;
  gap: var(--tile-gap);
}
</style>
