<script setup lang="ts">
import type { LetterState } from '../engine/types'
import KeyboardKey from './KeyboardKey.vue'

defineProps<{
  keyboardState: Map<string, LetterState[]>
}>()

const emit = defineEmits<{
  key: [letter: string]
  enter: []
  backspace: []
}>()

const rows = [
  ['q', 'w', 'e', 'r', 't', 'y', 'u', 'i', 'o', 'p'],
  ['a', 's', 'd', 'f', 'g', 'h', 'j', 'k', 'l'],
  ['z', 'x', 'c', 'v', 'b', 'n', 'm'],
]
</script>

<template>
  <div class="keyboard">
    <div class="keyboard-row" v-for="(row, ri) in rows" :key="ri">
      <KeyboardKey
        v-for="letter in row"
        :key="letter"
        :label="letter"
        :states="keyboardState.get(letter)"
        @press="emit('key', letter)"
      />
      <KeyboardKey
        v-if="ri === 1"
        label="⌫"
        :wide="true"
        @press="emit('backspace')"
      />
      <KeyboardKey
        v-if="ri === 2"
        label="Enter"
        :wide="true"
        @press="emit('enter')"
      />
    </div>
  </div>
</template>

<style scoped>
.keyboard {
  width: 100%;
  max-width: var(--keyboard-max-width);
  padding: 0 8px 8px;
  flex: 0 1 calc(21dvh + 26px);
  min-height: 122px;
  container-type: size;
}

.keyboard-row {
  display: flex;
  gap: var(--key-gap);
  margin-bottom: var(--key-gap);
  justify-content: center;
  min-height: 0px;
}
</style>
