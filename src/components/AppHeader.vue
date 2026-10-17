<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { RotateCcw, CircleQuestionMark, Info, ChevronDown, ChartNoAxesColumn, Sun, Moon } from '@lucide/vue'
import type { GameMode } from '../engine/types'

defineProps<{
  isDark: boolean
  currentMode: GameMode
}>()

const emit = defineEmits<{
  'toggle-theme': []
  'show-help': []
  'show-info': []
  'show-stats': []
  'clear-game': []
  'change-mode': [GameMode]
}>()

const isDev = import.meta.env.DEV

const dropdownOpen = ref(false)
const selectorRef = ref<HTMLElement | null>(null)

function toggleDropdown() {
  dropdownOpen.value = !dropdownOpen.value
}

function selectMode(mode: GameMode) {
  dropdownOpen.value = false
  emit('change-mode', mode)
}

function onDocumentClick(e: MouseEvent) {
  if (selectorRef.value && !selectorRef.value.contains(e.target as Node)) {
    dropdownOpen.value = false
  }
}

onMounted(() => document.addEventListener('click', onDocumentClick))
onUnmounted(() => document.removeEventListener('click', onDocumentClick))
</script>

<template>
  <header class="header">
    <div class="header-left">
      <button v-if="isDev" v-blur-on-click class="icon-btn debug-btn" @click="$emit('clear-game')" aria-label="Debug: limpar jogo" title="Debug: limpar jogo">
        <RotateCcw :size="20" />
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('show-help')" aria-label="Ajuda">
        <CircleQuestionMark :size="24" />
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('show-info')" aria-label="Sobre">
        <Info :size="24" />
      </button>
    </div>

    <div ref="selectorRef" class="mode-selector">
      <button v-blur-on-click class="mode-btn" @click="toggleDropdown" :aria-expanded="dropdownOpen">
        {{ currentMode.toUpperCase() }}
        <ChevronDown class="chevron" :class="{ open: dropdownOpen }" :size="14" :stroke-width="3" />
      </button>
      <div v-if="dropdownOpen" class="mode-dropdown">
        <button
          v-for="m in ['termo', 'dueto', 'quarteto'] as GameMode[]"
          :key="m"
          class="dropdown-item"
          :class="{ active: m === currentMode }"
          @click="selectMode(m)"
        >
          {{ m.toUpperCase() }}
        </button>
      </div>
    </div>

    <div class="header-right">
      <button v-blur-on-click class="icon-btn" @click="$emit('show-stats')" aria-label="Estatísticas">
        <ChartNoAxesColumn :size="24" />
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('toggle-theme')" aria-label="Tema">
        <Sun v-if="isDark" :size="24" />
        <Moon v-else :size="24" />
      </button>
    </div>
  </header>
</template>

<style scoped>
.header {
  width: 100%;
  max-width: 720px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  height: 50px;
  border-bottom: 1px solid var(--color-header-border);
  flex-shrink: 0;
}

.header-left,
.header-right {
  display: flex;
  gap: 4px;
  min-width: 70px;
}

.header-right {
  justify-content: flex-end;
}

.mode-selector {
  position: relative;
}

.mode-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  color: var(--color-text);
  font-size: 28px;
  font-weight: 700;
  letter-spacing: 0.1em;
  padding: 4px 6px;
  border-radius: 4px;
  line-height: 1;
}

.mode-btn:hover {
  opacity: 0.7;
}

.chevron {
  transition: transform 0.15s ease;
  flex-shrink: 0;
  margin-top: 2px;
}

.chevron.open {
  transform: rotate(180deg);
}

.mode-dropdown {
  position: absolute;
  top: calc(100% + 6px);
  left: 50%;
  transform: translateX(-50%);
  background: var(--color-modal-bg);
  border: 1px solid var(--color-header-border);
  border-radius: 6px;
  overflow: hidden;
  z-index: 100;
  min-width: 120px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.dropdown-item {
  display: block;
  width: 100%;
  padding: 10px 16px;
  text-align: center;
  background: none;
  color: var(--color-text);
  font-size: 16px;
  font-weight: 700;
  letter-spacing: 0.08em;
}

.dropdown-item:hover {
  background: var(--color-header-border);
}

.dropdown-item.active {
  color: var(--color-correct);
}

.icon-btn {
  background: none;
  color: var(--color-text);
  padding: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.icon-btn:hover {
  opacity: 0.7;
}

.debug-btn {
  color: #e66;
}
</style>
