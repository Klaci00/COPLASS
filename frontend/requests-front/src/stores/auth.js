// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem('token') || null)
  const is_staff = ref(localStorage.getItem('is_staff') === 'true')
  const hr_id  = ref(localStorage.getItem('hr_id') || null)
  const user_name  = ref(localStorage.getItem('user_name') || null)

  const is_logged_in = computed(() => !!token.value)
  const display_name = computed(() =>
    hr_id.value && user_name.value ? `${user_name.value} #${hr_id.value}` : 'Guest'
  )

  function login(data) {
    token.value = data.token
    is_staff.value = data.is_staff
    hr_id.value  = data.hr_id
    user_name.value  = data.name
    localStorage.setItem('token', data.token)
    localStorage.setItem('is_staff', data.is_staff.toString())
    localStorage.setItem('hr_id', data.hr_id)
    localStorage.setItem('user_name', data.name)
  }

  function logout() {
    token.value = null
    hr_id.value  = null
    user_name.value  = null
    is_staff.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('hr_id  ')
    localStorage.removeItem('user_name')
    localStorage.removeItem('is_staff')
  }
  
  return { token, hr_id, user_name, is_logged_in, display_name,is_staff, login, logout }
})