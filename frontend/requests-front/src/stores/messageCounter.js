import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi'
import { useAuthStore } from './auth'

export const useMessageCounterStore = defineStore('messageCounter', () => {
  const unreadCount = ref(0)

  const fetchUnreadCount = async () => {
    const { get } = useApi()       // ✅ instantiated inside the function, not at store root
    const auth = useAuthStore()    // ✅ same — avoids circular store reference issues

    if (!auth.is_logged_in) return   // ✅ guard: don't fetch if not logged in

    try {
      const res = await get(`/messages/?employee_id=${auth.hr_id}`)
      if (res.ok) {
        const data = await res.json()
        unreadCount.value = data.filter(m => !m.is_read).length
      }
    } catch {}
  }

  function decrement() {
    if (unreadCount.value > 0) unreadCount.value--  // ✅ guard against going negative
  }

  function reset() {
    unreadCount.value = 0  // ✅ useful on logout
  }

  return { unreadCount, fetchUnreadCount, decrement, reset }
})