import { ref } from 'vue'
import { defineStore } from 'pinia'
import { useApi } from '../composables/useApi'
import { useAuthStore } from './auth'

export const useRequestCounterStore = defineStore('requestCounter', () => {
  const unapprovedCount = ref(0)

  const fetchunapprovedCount = async () => {
    const { get } = useApi() // ✅ instantiated inside the function, not at store root
    const auth = useAuthStore() // ✅ same — avoids circular store reference issues

    if (!auth.is_logged_in) return // ✅ guard: don't fetch if not logged in

    try {
      const res = await get('/access-right-requests/')
      if (res.ok) {
        const data = await res.json()
        console.log('Fetched access right requests:', data) // ✅ debug log
        unapprovedCount.value = data.filter((m) => !m.approved).length
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
