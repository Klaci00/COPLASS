// src/stores/auth.js
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { STORAGE_KEYS } from '../constants/storageKeys'

export const useAuthStore = defineStore('auth', () => {
  const token = ref(localStorage.getItem(STORAGE_KEYS.TOKEN) || null)
  const is_staff = ref(localStorage.getItem(STORAGE_KEYS.IS_STAFF) === 'true')
  const hr_id  = ref(localStorage.getItem(STORAGE_KEYS.HR_ID) || null)
  const user_name  = ref(localStorage.getItem(STORAGE_KEYS.USER_NAME) || null)
  const is_supervisor = ref(localStorage.getItem(STORAGE_KEYS.IS_SUPERVISOR) === 'true')
  const department = ref(localStorage.getItem(STORAGE_KEYS.DEPARTMENT) || null)
  const is_logged_in = computed(() => !!token.value)
  const display_name = computed(() =>
    hr_id.value && user_name.value ? `${user_name.value} #${hr_id.value}` : 'Guest'
  )

  function login(data) {
    token.value = data.token
    is_staff.value = data.is_staff
    hr_id.value  = data.hr_id
    user_name.value  = data.user_name
    is_supervisor.value = data.is_supervisor
    department.value = data.department
    localStorage.setItem(STORAGE_KEYS.TOKEN, data.token)
    localStorage.setItem(STORAGE_KEYS.IS_STAFF, data.is_staff.toString())
    localStorage.setItem(STORAGE_KEYS.HR_ID, data.hr_id)
    localStorage.setItem(STORAGE_KEYS.USER_NAME, data.user_name)
    localStorage.setItem(STORAGE_KEYS.IS_SUPERVISOR, data.is_supervisor.toString())
    localStorage.setItem(STORAGE_KEYS.DEPARTMENT, data.department)
  }

  function logout() {
    token.value = null
    hr_id.value  = null
    user_name.value  = null
    is_staff.value = null
    is_supervisor.value = null
    department.value = null
    localStorage.removeItem(STORAGE_KEYS.TOKEN  )
    localStorage.removeItem(STORAGE_KEYS.HR_ID)
    localStorage.removeItem(STORAGE_KEYS.USER_NAME)
    localStorage.removeItem(STORAGE_KEYS.IS_STAFF)
    localStorage.removeItem(STORAGE_KEYS.IS_SUPERVISOR)
    localStorage.removeItem(STORAGE_KEYS.DEPARTMENT)
  }
  
  return { token, hr_id, user_name, is_logged_in, display_name,is_staff, is_supervisor, department, login, logout }
})