// src/composables/useTheme.js
import { ref, watch } from 'vue'

const isDark = ref(localStorage.getItem('theme') === 'dark')

// Apply the class to <html> whenever isDark changes
watch(isDark, (dark) => {
  document.documentElement.classList.toggle('dark', dark)
  console.log(`Theme changed to: ${dark ? 'dark' : 'light'}`)
  localStorage.setItem('theme', dark ? 'dark' : 'light')
}, { immediate: true })

export function useTheme() {
  const toggle = () => { isDark.value = !isDark.value }
  return { isDark, toggle }
}