import { ref, watchEffect } from 'vue'

export function useTheme() {
  const isDark = ref(
    localStorage.getItem('termo-pt-theme') === 'dark' ||
      (!localStorage.getItem('termo-pt-theme') &&
        window.matchMedia('(prefers-color-scheme: dark)').matches),
  )

  watchEffect(() => {
    document.documentElement.setAttribute(
      'data-theme',
      isDark.value ? 'dark' : 'light',
    )
    localStorage.setItem('termo-pt-theme', isDark.value ? 'dark' : 'light')
  })

  function toggle() {
    isDark.value = !isDark.value
  }

  return { isDark, toggle }
}
