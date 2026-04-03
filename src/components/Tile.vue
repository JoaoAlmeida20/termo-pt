<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { LetterState } from '../engine/types'

const props = defineProps<{
  letter: string
  state: LetterState | 'empty' | 'input'
  delay?: number
  reveal?: boolean
  bounce?: boolean
  bounceDelay?: number
  isCursor?: boolean
  waiting?: boolean
}>()

const revealed = ref(!props.reveal)
const showState = ref(!props.reveal)

onMounted(() => {
  if (!props.reveal) return
  const delay = props.delay ?? 0
  // After staggered delay, start the flip-in (hide front)
  setTimeout(() => {
    revealed.value = true
    // At midpoint of flip, switch to colored state
    setTimeout(() => {
      showState.value = true
    }, 250)
  }, delay)
})
</script>

<template>
  <div
    class="tile"
    :class="[
      waiting ? 'tile--waiting' : (showState ? `tile--${state}` : (state === 'input' || state === 'empty' ? `tile--${state}` : 'tile--empty')),
      { 'tile--pop': state === 'input' && letter },
      { 'tile--unpop': state === 'empty' && !letter },
      { 'tile--flip': reveal && revealed },
      { 'tile--bounce': bounce },
      { 'tile--cursor': isCursor },
    ]"
    :style="{
      animationDelay: bounce ? `${bounceDelay ?? 0}ms` : undefined,
    }"
  >
    {{ letter }}
  </div>
</template>

<style scoped>
.tile {
  width: var(--tile-size);
  height: var(--tile-size);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: calc(var(--tile-size) * 0.57);
  font-weight: 600;
  text-transform: uppercase;
  border: max(1px, calc(var(--tile-size) * 0.07)) solid var(--color-tile-border);
  border-radius: max(2px, calc(var(--tile-size) * 0.1));
  user-select: none;
}

.tile--empty {
  border-color: var(--color-tile-border);
}

.tile--waiting {
  background-color: var(--color-tile-waiting);
  border-color: var(--color-tile-waiting);
}

.tile--input {
  border-color: var(--color-tile-border-active);
}

.tile--correct {
  background-color: var(--color-correct);
  color: var(--color-tile-text);
  border-color: var(--color-correct);
}

.tile--present {
  background-color: var(--color-present);
  color: var(--color-tile-text);
  border-color: var(--color-present);
}

.tile--absent {
  background-color: var(--color-absent);
  color: var(--color-tile-text);
  border-color: var(--color-absent);
}

.tile--cursor {
  border-bottom-width: max(2px, calc(var(--tile-size) * 0.15));
}

.tile--cursor.tile--pop {
  animation: pop 0.2s ease-in, cursor 0.2s ease-out;
}

.tile--cursor.tile--unpop {
  animation: unpop 0.2s ease-out, cursor 0.2s ease-out;
}

.tile--pop {
  animation: pop 0.2s ease-in;
}

.tile--unpop {
  animation: unpop 0.2s ease-out;
}

.tile--flip {
  animation: flip 0.6s ease;
}

.tile--bounce {
  animation: bounce 1s;
}
</style>
