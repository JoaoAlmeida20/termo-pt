<script setup lang="ts">
import { ref, computed } from 'vue'
import type { PlayerStats, GameStatus } from '../engine/types'
import ModalOverlay from './ModalOverlay.vue'

const props = defineProps<{
  stats: PlayerStats
  gameStatus: GameStatus
  guessCount: number
  shareText: string
  answers: string[]
}>()

defineEmits<{
  close: []
}>()

const copied = ref(false)

function share() {
  navigator.clipboard.writeText(props.shareText).then(() => {
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  })
}

function winPercent() {
  if (props.stats.gamesPlayed === 0) return 0
  return Math.round((props.stats.gamesWon / props.stats.gamesPlayed) * 100)
}

const lossCount = computed(() => Math.max(0, props.stats.gamesPlayed - props.stats.gamesWon))

function maxDistribution() {
  return Math.max(...props.stats.guessDistribution, lossCount.value, 1)
}
</script>

<template>
  <ModalOverlay @close="$emit('close')">
    <h2 class="stats-title">Estatísticas</h2>

    <div class="stats-row">
      <div class="stat">
        <div class="stat-value">{{ stats.gamesPlayed }}</div>
        <div class="stat-label">Jogos</div>
      </div>
      <div class="stat">
        <div class="stat-value">{{ winPercent() }}%</div>
        <div class="stat-label">de Vitórias</div>
      </div>
      <div class="stat">
        <div class="stat-value">{{ stats.currentStreak }}</div>
        <div class="stat-label">Sequência de vitórias atual</div>
      </div>
      <div class="stat">
        <div class="stat-value">{{ stats.maxStreak }}</div>
        <div class="stat-label">Melhor sequência de vitórias</div>
      </div>
    </div>

    <h3 class="dist-title">Distribuição</h3>
    <div class="distribution">
      <div
        v-for="(count, i) in stats.guessDistribution"
        :key="i"
        class="dist-row"
      >
        <span class="dist-label">{{ i + 1 }}</span>
        <div
          class="dist-bar"
          :class="{
            'dist-bar--today': gameStatus === 'won' && i === guessCount - 1,
            'dist-bar--empty': count === 0,
          }"
          :style="count > 0 ? { width: `${Math.max((count / maxDistribution()) * 100, 7)}%` } : {}"
        >
          {{ count }}
        </div>
      </div>
      <div class="dist-row">
        <span class="dist-label">💀</span>
        <div
          class="dist-bar"
          :class="{
            'dist-bar--loss': gameStatus === 'lost',
            'dist-bar--empty': lossCount === 0,
          }"
          :style="lossCount > 0 ? { width: `${Math.max((lossCount / maxDistribution()) * 100, 7)}%` } : {}"
        >
          {{ lossCount }}
        </div>
      </div>
    </div>

    <div v-if="gameStatus === 'lost'" class="answer-reveal">
      {{ answers.length === 1 ? 'A palavra era' : 'As palavras eram' }}:
      <strong>{{ answers.join(', ') }}</strong>
    </div>

    <button
      v-if="gameStatus !== 'playing'"
      v-blur-on-click
      class="share-btn"
      @click="share"
    >
      {{ copied ? 'Copiado!' : 'Partilhar' }}
    </button>
  </ModalOverlay>
</template>

<style scoped>
.stats-title,
.dist-title {
  text-align: center;
  margin-bottom: 12px;
}

.dist-title {
  margin-top: 20px;
  font-size: 14px;
  text-transform: uppercase;
}

.stats-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 20px 8px;
}

.stat {
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  line-height: 1;
}

.stat-label {
  font-size: 15px;
  line-height: 1.3;
  max-width: 100px;
}

.distribution {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.dist-row {
  display: flex;
  align-items: center;
  gap: 4px;
}

.dist-label {
  font-size: 17px;
  font-weight: 700;
  width: 20px;
  text-align: center;
  flex-shrink: 0;
}


.dist-bar {
  background: var(--color-absent);
  color: var(--color-tile-text);
  font-size: 17px;
  font-weight: 700;
  padding: 2px 8px;
  text-align: right;
  min-width: 24px;
  border-radius: 2px;
}

.dist-bar--today {
  background: var(--color-correct);
}

.dist-bar--loss {
  background: var(--color-wrong);
}

.dist-bar--empty {
  background: transparent;
  color: var(--color-absent);
  min-width: 0;
}

.answer-reveal {
  text-align: center;
  margin-top: 16px;
  font-size: 16px;
  text-transform: uppercase;
}

.share-btn {
  display: block;
  margin: 20px auto 0;
  padding: 12px 32px;
  background: var(--color-correct);
  color: white;
  font-size: 18px;
  font-weight: 700;
  border-radius: 4px;
  text-transform: uppercase;
}

.share-btn:hover {
  opacity: 0.9;
}
</style>
