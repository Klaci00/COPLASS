<template>
  <div class="auth-card">
    <h1>Welcome back</h1>
    <p class="subtitle">Sign in with your HR ID</p>

    <form @submit.prevent="handleLogin">
      <div class="form-group">
        <label for="username">HR ID</label>
        <input
          id="username"
          v-model="username"
          type="text"
          placeholder="e.g. 1042"
          required
          autocomplete="username"
        />
      </div>
      <div class="form-group">
        <label for="password">Password</label>
        <input
          id="password"
          v-model="password"
          type="password"
          placeholder="••••••••"
          required
          autocomplete="current-password"
        />
      </div>

      <p v-if="errorMessage" class="feedback error">{{ errorMessage }}</p>

      <button type="submit" class="btn-primary" :disabled="isLoading">
        {{ isLoading ? 'Signing in…' : 'Sign in' }}
      </button>
    </form>

    <p class="auth-footer">No account? <router-link to="/register">Register here</router-link></p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useApi } from '../composables/useApi'
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
const { post } = useApi()
const router = useRouter()
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const isLoading = ref(false)

const handleLogin = async () => {
  isLoading.value = true
  errorMessage.value = ''
  try {
    const response = await post(
      '/login/',
      { username: username.value, password: password.value },
      false,
    )
    console.log(username.value, password.value) // Debugging statement
    if (!response.ok) throw new Error()
    const data = await response.json()
    auth.login({
      token: data.token,
      is_staff: data.is_staff,
      hr_id: data.hr_id,
      user_name: data.user_name,
      is_supervisor: data.is_supervisor,
      department: data.department,
    })
    router.push('/dashboard')
  } catch {
    errorMessage.value = 'Invalid HR ID or password.'
  } finally {
    isLoading.value = false
  }
}
</script>
