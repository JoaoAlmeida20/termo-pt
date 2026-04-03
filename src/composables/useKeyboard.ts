import { onMounted, onUnmounted } from 'vue'

export function useKeyboard(handlers: {
  onLetter: (letter: string) => void
  onEnter: () => void
  onBackspace: () => void
  onArrowLeft?: () => void
  onArrowRight?: () => void
}) {
  function handleKeydown(e: KeyboardEvent) {
    if (e.ctrlKey || e.metaKey || e.altKey) return
    if (e.key === 'Enter') {
      handlers.onEnter()
      return
    }
    if (e.key === 'Backspace') {
      handlers.onBackspace()
      return
    }
    if (e.key === 'ArrowLeft') {
      e.preventDefault()
      handlers.onArrowLeft?.()
      return
    }
    if (e.key === 'ArrowRight') {
      e.preventDefault()
      handlers.onArrowRight?.()
      return
    }
    if (/^[a-z]$/i.test(e.key)) {
      handlers.onLetter(e.key.toLowerCase())
    }
  }

  onMounted(() => window.addEventListener('keydown', handleKeydown))
  onUnmounted(() => window.removeEventListener('keydown', handleKeydown))
}
