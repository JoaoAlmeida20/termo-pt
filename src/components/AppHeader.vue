<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
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
        <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="3 5 3 11 10 11"/>
          <path d="M3.51 15 a9 9 0 1 0 .49 -4.46"/>
        </svg>
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('show-help')" aria-label="Ajuda">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('show-info')" aria-label="Sobre">
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="10"/>
          <line x1="12" y1="8" x2="12" y2="8.01"/>
          <line x1="12" y1="12" x2="12" y2="16"/>
        </svg>
      </button>
    </div>

    <div ref="selectorRef" class="mode-selector">
      <button v-blur-on-click class="mode-btn" @click="toggleDropdown" :aria-expanded="dropdownOpen">
        {{ currentMode.toUpperCase() }}
        <svg class="chevron" :class="{ open: dropdownOpen }" xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="6 9 12 15 18 9"/>
        </svg>
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
        <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <line x1="18" y1="20" x2="18" y2="10"/>
          <line x1="12" y1="20" x2="12" y2="4"/>
          <line x1="6" y1="20" x2="6" y2="14"/>
        </svg>
      </button>
      <button v-blur-on-click class="icon-btn" @click="$emit('toggle-theme')" aria-label="Tema">
        <svg v-if="isDark" xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <circle cx="12" cy="12" r="5"/>
          <line x1="12" y1="1" x2="12" y2="3"/>
          <line x1="12" y1="21" x2="12" y2="23"/>
          <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/>
          <line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
          <line x1="1" y1="12" x2="3" y2="12"/>
          <line x1="21" y1="12" x2="23" y2="12"/>
          <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/>
          <line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
        </svg>
        <svg v-else xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
          <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
        </svg>
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
