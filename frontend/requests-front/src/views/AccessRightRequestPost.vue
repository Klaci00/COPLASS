<template>
  <div class="form-container">
    <h2>Create Access Right Request</h2>
    
    <form @submit.prevent="submitRequest">
      <!-- Security Zone Dropdown -->
      <div class="form-group">
        <label>Security Zone*:</label>
        <select v-model="formData.security_zone" required>
          <option value="" disabled>Select a security zone</option>
          <option v-for="zone in securityZones" :key="zone.id" :value="zone.id">
            {{ zone.name || `Zone #${zone.id}` }}
          </option>
        </select>
      </div>

      <!-- Start Date Picker -->
      <div class="form-group">
        <label>Start Date*:</label>
        <input type="date" v-model="formData.start_date" required />
      </div>

      <!-- End Date Picker -->
      <div class="form-group">
        <label>End Date*:</label>
        <input type="date" v-model="formData.end_date" required />
      </div>

      <div class="form-group">
        <label>Employee*:</label>
        <select v-model="formData.employee" required>
          <option :value="null">-- No Employee Assigned --</option>
          <option v-for="emp in employees" :key="emp.id" :value="emp.id">
            {{ emp.name || `Employee #${emp.id}` }}
          </option>
        </select>
      </div>

      <!-- Status Messages -->
      <p v-if="submitError" class="error">{{ submitError }}</p>
      <p v-if="submitSuccess" class="success">Request created successfully!</p>

      <button type="submit" :disabled="isSubmitting">
        {{ isSubmitting ? 'Submitting...' : 'Submit Request' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'

// 1. Reactive state for our dropdown data
const securityZones = ref([])
const employees = ref([])

// 2. Reactive state for the form payload
const formData = ref({
  security_zone: '',
  start_date: '',
  end_date: '',
  employee: null // Can be null because blank=True, null=True in Django
})

// 3. UI State
const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

// 4. Helper to get Auth Token for our requests
const getHeaders = () => {
  const token = localStorage.getItem('token')
  return {
    'Content-Type': 'application/json',
    'Authorization': `Token ${token}`
  }
}

// 5. Fetch dropdown options when the component loads
onMounted(async () => {
  try {
    const [zoneRes, empRes] = await Promise.all([
      fetch('http://127.0.0.1:8000/api/security_zones/', { headers: getHeaders() }),
      fetch('http://127.0.0.1:8000/api/employees/', { headers: getHeaders() })
    ])
    
    // Note: If you are using Django Rest Framework Pagination, you may need to map 
    // `await zoneRes.json().then(data => data.results)` instead
    securityZones.value = await zoneRes.json()
    employees.value = await empRes.json()
  } catch (error) {
    console.error('Failed to load dropdown data:', error)
  }
})

// 6. Handle Form Submission
const submitRequest = async () => {
  isSubmitting.value = true
  submitError.value = ''
  submitSuccess.value = false

  try {
    const response = await fetch('http://127.0.0.1:8000/api/access_right_requests/', {
      method: 'POST',
      headers: getHeaders(),
      body: JSON.stringify(formData.value) // Vue automatically matches the Django fields
    })

    if (!response.ok) {
      const errorData = await response.json()
      throw new Error(JSON.stringify(errorData))
    }

    submitSuccess.value = true
    
    // Optional: Reset form after success
    formData.value = {
      security_zone: '',
      start_date: '',
      end_date: '',
      employee: null
    }
  } catch (error) {
    submitError.value = 'Failed to submit: ' + error.message
  } finally {
    isSubmitting.value = false
  }
}
</script>

<style scoped>
.form-container {
  max-width: 500px;
  margin: 0 auto;
  padding: 20px;
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}
.form-group {
  margin-bottom: 15px;
  display: flex;
  flex-direction: column;
}
.form-group label {
  margin-bottom: 5px;
  font-weight: bold;
}
.form-group input, .form-group select {
  padding: 8px;
  border: 1px solid #ccc;
  border-radius: 4px;
}
button {
  width: 100%;
  padding: 10px;
  background-color: #42b983;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
}
button:disabled {
  background-color: #a0d8c0;
}
.error { color: red; }
.success { color: green; }
</style>