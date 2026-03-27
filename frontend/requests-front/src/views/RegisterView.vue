<template>
  <div class="register-container">
    <h2>Employee Registration</h2>
    
    <form @submit.prevent="handleRegister">
      <div class="form-group">
        <label>First Name:</label>
        <input type="text" v-model="formData.firstname" required />
      </div>

      <div class="form-group">
        <label>Last Name:</label>
        <input type="text" v-model="formData.lastname" required />
      </div>

      <div class="form-group">
        <label>Date of Birth:</label>
        <input type="date" v-model="formData.date_of_birth" required />
      </div>

      <div class="form-group">
        <label>Department:</label>
        <input type="text" v-model="formData.department" required />
      </div>

      <div class="form-group">
        <label>Password:</label>
        <input type="password" v-model="formData.password" required />
      </div>
      
      <div class="form-group">
        <label>Confirm Password:</label>
        <input type="password" v-model="formData.confirm_password" required />
      </div>

      <!-- Status Messages -->
      <p v-if="submitError" class="error">{{ submitError }}</p>
      <div v-if="submitSuccess" class="success">
        <p>Registration successful!</p>
        <router-link to="/login">Click here to log in</router-link>
      </div>

      <button type="submit" :disabled="isSubmitting || !isPasswordMatch || submitSuccess">
        {{ isSubmitting ? 'Registering...' : 'Register' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

// Match the exact keys expected by your Django view
const formData = ref({
  firstname: '',
  lastname: '',
  date_of_birth: '',
  department: '',
  password: '',
  confirm_password: ''
})

const isPasswordMatch = computed(() => formData.value.password === formData.value.confirm_password)
const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

const handleRegister = async () => {
  isPasswordMatch.value = formData.value.password === formData.value.confirm_password
  isSubmitting.value = true
  submitError.value = ''
  submitSuccess.value = false

  try {
    // Make sure to match this URL to your actual Django urls.py path
    const response = await fetch('http://127.0.0.1:8000/api/register_employee/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(formData.value)
    })

    const data = await response.json()

    if (!response.ok) {
      // Catch errors returned by your view's except block or standard DRF validation
      throw new Error(data.error || 'Registration failed')
    }

    // Success! 
    submitSuccess.value = true
    
    // Clear the form
    formData.value = {
      firstname: '',
      lastname: '',
      date_of_birth: '',
      department: '',
      password: '',
      confirm_password: '',

    }

  } catch (error) {
    submitError.value = error.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 40px auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 5px;
  font-weight: 600;
  color: #333;
}
.form-group input {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
}
button {
  width: 100%;
  padding: 12px;
  background-color: #007bff;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  margin-top: 10px;
}
button:disabled {
  background-color: #99c2ff;
  cursor: not-allowed;
}
.error { color: #dc3545; font-weight: bold; }
.success { color: #28a745; text-align: center; font-weight: bold; }
.success a { color: #007bff; text-decoration: underline; }
</style>