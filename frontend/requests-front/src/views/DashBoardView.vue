<template>
  <div class="dashboard-container">
    <h2>Welcome to your Dashboard!</h2>
    <p>You have successfully logged in and received a token from Django.</p>

    <button @click="handleLogout" class="logout-btn">Logout</button>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router'

const router = useRouter()

const handleLogout = () => {
  // 1. Remove the token from local storage
  localStorage.removeItem('token')
  localStorage.removeItem('is_logged_in')

  // 2. Redirect the user back to the login page
  router.push('/login')
}
</script>

<style scoped>
.dashboard-container {
  text-align: center;
  margin-top: 50px;
  padding: 20px;
  border: 1px solid #ddd;
  border-radius: 8px;
  background-color: #f9f9f9;
}

.logout-btn {
  margin-top: 20px;
  padding: 10px 20px;
  background-color: #dc3545;
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
  font-weight: bold;
}

.logout-btn:hover {
  background-color: #c82333;
}
</style>
