<script setup lang="ts">
import ModalOverlay from './ModalOverlay.vue'

defineEmits<{
  close: []
}>()
</script>

<template>
  <ModalOverlay @close="$emit('close')">
    <h2 class="info-title">Sobre o Termo PT</h2>

    <p>
      <strong>Termo PT</strong> é uma versão para Português de Portugal do
      <a href="https://www.nytimes.com/games/wordle/index.html" target="_blank" rel="noopener">Wordle</a>,
      originalmente criado por 
      <a href="https://www.powerlanguage.co.uk/" target="_blank" rel="noopener">Josh Wardle</a>.
    </p>
    
    <div class="credit-item">
      <p>
        Inspirado no
        <a href="https://term.ooo" target="_blank" rel="noopener">Termo</a>,
        o Wordle para Português do Brasil, criado por
        <a href="https://fserb.com" target="_blank" rel="noopener">Fernando Serboncini</a>.
      </p>
    </div>

    <div class="credit-item">
      <p>
        Lista de palavras baseada no léxico
        <a href="https://www.psi.uminho.pt/pt/CIPsi/Laboratorios_Investigacao/Psicolinguistica/Paginas/Bases_Lexiais_Estudos_Normativos.aspx" target="_blank" rel="noopener">SUBTLEX-PT</a>
        para Português Europeu, derivado de legendas de cinema e televisão, construído por investigadores da Universidade do Minho:
      </p>
      <p class="citation">
        Soares, A.&nbsp;P., Machado, J., Costa, A., Iriarte, A., Simões, A., de Almeida, J.&nbsp;J.,
        Comesaña, M., &amp; Perea, M. (2015). On the advantages of frequency measures extracted
        from subtitles: The case of Portuguese. <em>Quarterly Journal of Experimental
        Psychology</em>, <em>68</em>, 680–696.
      </p>
    </div>
  </ModalOverlay>
</template>

<style scoped>
.info-title {
  text-align: center;
  margin-bottom: 16px;
}

p {
  margin-bottom: 8px;
  font-size: 14px;
  line-height: 1.5;
}

a {
  color: var(--color-correct);
  text-decoration: underline;
  text-underline-offset: 2px;
}

a:hover {
  opacity: 0.8;
}

.section {
  margin-top: 16px;
  border-top: 1px solid var(--color-header-border);
  padding-top: 16px;
}

.section h3 {
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 12px;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  opacity: 0.6;
}

.credit-item {
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--color-header-border);
}

.credit-item:last-child {
  border-bottom: none;
  margin-bottom: 0;
  padding-bottom: 0;
}

.citation {
  font-size: 12px;
  opacity: 0.7;
  font-style: normal;
  margin-top: 6px;
  padding: 8px;
  border-radius: 4px;
  line-height: 1.5;
}
</style>
