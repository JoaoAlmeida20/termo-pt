<script setup lang="ts">
import ModalOverlay from './ModalOverlay.vue'

defineEmits<{
  close: []
}>()
</script>

<template>
  <ModalOverlay @close="$emit('close')">
    <h2 class="help-title">Como Jogar</h2>
    <p>Adivinha a palavra em 6 tentativas.</p>
    <p>Cada tentativa tem de ser uma palavra válida de 5 letras. Carrega em Enter para submeter.</p>
    <p>Depois de submeter, as cores das letras mudam para mostrar o quão perto está da palavra.</p>

    <div class="examples">
      <p><strong>Exemplos</strong></p>

      <div class="example-row">
        <div class="ex-tile ex-correct">F</div>
        <div class="ex-tile">A</div>
        <div class="ex-tile">L</div>
        <div class="ex-tile">A</div>
        <div class="ex-tile">R</div>
      </div>
      <p class="example-desc">A letra <strong>F</strong> está na palavra e na posição correta.</p>

      <div class="example-row">
        <div class="ex-tile">C</div>
        <div class="ex-tile ex-present">A</div>
        <div class="ex-tile">S</div>
        <div class="ex-tile">A</div>
        <div class="ex-tile">S</div>
      </div>
      <p class="example-desc">A letra <strong>A</strong> está na palavra mas numa posição diferente.</p>

      <div class="example-row">
        <div class="ex-tile">P</div>
        <div class="ex-tile">E</div>
        <div class="ex-tile">D</div>
        <div class="ex-tile">R</div>
        <div class="ex-tile ex-absent">A</div>
      </div>
      <p class="example-desc">A letra <strong>A</strong> não está na palavra.</p>
    </div>

    <div class="accent-note">
      <p><strong>Nota sobre acentos:</strong> Não é preciso escrever acentos ou ç. Basta escrever a letra sem acento (por exemplo, escreve "cacao" para "cação"). As letras com acento aparecem automaticamente depois de submeter.</p>
    </div>
  </ModalOverlay>
</template>

<style scoped>
.help-title {
  text-align: center;
  margin-bottom: 16px;
}

p {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.4;
}

.examples {
  margin-top: 16px;
  border-top: 1px solid var(--color-header-border);
  padding-top: 16px;
}

.example-row {
  display: flex;
  gap: 4px;
  margin: 8px 0;
}

.ex-tile {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
  font-weight: 700;
  border: 2px solid var(--color-tile-border);
}

.ex-correct {
  background-color: var(--color-correct);
  color: var(--color-tile-text);
  border-color: var(--color-correct);
}

.ex-present {
  background-color: var(--color-present);
  color: var(--color-tile-text);
  border-color: var(--color-present);
}

.ex-absent {
  background-color: var(--color-absent);
  color: var(--color-tile-text);
  border-color: var(--color-absent);
}

.example-desc {
  font-size: 13px;
}

.accent-note {
  margin-top: 16px;
  border-top: 1px solid var(--color-header-border);
  padding-top: 16px;
}
</style>
