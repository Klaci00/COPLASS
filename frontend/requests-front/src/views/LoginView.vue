<template>
  <div class="login-container">
    <h2>Login to Django</h2>
    <form @submit.prevent="handleLogin">
      <div>
        <label>HR-ID: </label>
        <input v-model="username" type="text" required />
      </div>
      <div>
        <label>Password: </label>
        <input v-model="password" type="password" required />
      </div>
      <button type="submit">Login</button>
    </form>
    <p v-if="errorMessage" style="color: red;">{{ errorMessage }}</p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

// Reactive variables to store user input
const username = ref('')
const password = ref('')
const errorMessage = ref('')
const router = useRouter()

const handleLogin = async () => {
  try {
    // Replace with your actual Django API URL
    const response = await fetch('http://localhost:8000/api/login/', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: username.value,
        password: password.value
      })
    })

    if (!response.ok) {
      throw new Error('Invalid credentials')
    }

    const data = await response.json()
    
    // Save the authentication token to the browser's local storage
    localStorage.setItem('token', data.token)
    
    // Redirect the user to a secure dashboard page after successful login
    router.push('/dashboard')
    
  } catch (error) {
    errorMessage.value = 'Login failed. Please check your credentials.'
  }
}
</script>