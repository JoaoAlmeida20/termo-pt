<script setup lang="ts">
import { computed } from 'vue'
import type { LetterState } from '../engine/types'

const props = defineProps<{
  label: string
  states?: LetterState[]  // undefined = unguessed; length 1 = termo; 2 = dueto; 4 = quarteto
  wide?: boolean
}>()

defineEmits<{
  press: []
}>()

// Positions for segment slots based on count
const segmentPositions: Record<number, string[]> = {
  2: ['left', 'right'],
  4: ['top-left', 'top-right', 'bottom-left', 'bottom-right'],
}

const isSplit = computed(() => props.states !== undefined && props.states.length > 1)

const singleState = computed<LetterState | undefined>(() => {
  if (!props.states || props.states.length !== 1) return undefined
  return props.states[0]
})

const segments = computed(() => {
  if (!isSplit.value || !props.states) return []
  const positions = segmentPositions[props.states.length] ?? []
  return props.states.map((state, i) => ({ state, position: positions[i] ?? '' }))
})
</script>

<template>
  <button
    v-blur-on-click
    class="key"
    :class="[
      singleState ? `key--${singleState}` : '',
      { 'key--wide': wide, 'key--split': isSplit },
    ]"
    @click="$emit('press')"
    @mousedown.prevent
  >
    <span
      v-for="seg in segments"
      :key="seg.position"
      class="key-segment"
      :class="[`key-segment--${seg.position}`, `key-segment--${seg.state}`]"
    />
    <span class="key-label">{{ label }}</span>
  </button>
</template>

<style scoped>
.key {
  height: clamp(32px, calc((100cqh - 18px) / 3), 58px);
  min-width: 28px;
  padding: 0 4px;
  border-radius: 4px;
  background-color: var(--color-key-bg);
  color: var(--color-key-text);
  font-size: 13px;
  font-weight: 700;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  justify-content: center;
  flex: 1 1 clamp(32px, calc((100cqh - 18px) / 3), 58px);
  user-select: none;
  -webkit-tap-highlight-color: transparent;
  transition: background-color 0.1s;
}

.key--wide {
  flex: 1.5 1 calc(clamp(32px, calc((100cqh - 18px) / 3), 58px) * 1.5);
  font-size: 12px;
}

.key--correct {
  background-color: var(--color-correct);
  color: var(--color-tile-text);
}

.key--present {
  background-color: var(--color-present);
  color: var(--color-tile-text);
}

.key--absent {
  background-color: var(--color-absent);
  color: var(--color-tile-text);
}

.key:active {
  opacity: 0.8;
}

/* Split key layout */
.key--split {
  position: relative;
  overflow: hidden;
  color: var(--color-tile-text);
}

.key-segment {
  position: absolute;
  background-color: var(--color-key-bg);
}

.key-segment--left   { left: 0;   top: 0;    width: 50%; height: 100%; }
.key-segment--right  { right: 0;  top: 0;    width: 50%; height: 100%; }

.key-segment--top-left     { left: 0;   top: 0;    width: 50%; height: 50%; }
.key-segment--top-right    { right: 0;  top: 0;    width: 50%; height: 50%; }
.key-segment--bottom-left  { left: 0;   bottom: 0; width: 50%; height: 50%; }
.key-segment--bottom-right { right: 0;  bottom: 0; width: 50%; height: 50%; }

.key-segment--correct { background-color: var(--color-correct); }
.key-segment--present { background-color: var(--color-present); }
.key-segment--absent  { background-color: var(--color-absent); }

.key-label {
  position: relative;
  z-index: 1;
}
</style>
