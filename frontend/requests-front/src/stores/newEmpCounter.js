import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi'
import { useAuthStore } from './auth'

export const useNewEmpCounterStore = defineStore('newEmpCounter', () => {
  const unapprovedCount = ref(0)

  const fetchunapprovedCount = async () => {
    const { get } = useApi() // ✅ instantiated inside the function, not at store root
    const auth = useAuthStore() // ✅ same — avoids circular store reference issues

    if (!auth.is_logged_in) return // ✅ guard: don't fetch if not logged in

    try {
      const res = await get('/new-registrations/')
      if (res.ok) {
        const data = await res.json()

        unapprovedCount.value = data.filter((m) => !m.is_active).length
      }
    } catch (error) {
      console.error('Failed to fetch unapproved request count', error)
    }
  }

  function decrement() {
    if (unapprovedCount.value > 0) unapprovedCount.value-- // ✅ guard against going negative
  }

  function reset() {
    unapprovedCount.value = 0 // ✅ useful on logout
  }

  return { unapprovedCount, fetchunapprovedCount, decrement, reset }
})
