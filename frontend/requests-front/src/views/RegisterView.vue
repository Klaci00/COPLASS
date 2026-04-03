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
        <label>Department*:</label>
        <select v-model="formData.department" required @change="onSelectedDepartment">
          <option :value="null">-- No Department Assigned --</option>
          <option v-for="d in department" :key="d.id" :value="d.id">
            {{ d.name || `Department #${d.id}` }}
          </option>
        </select>
      </div>
      <div class="form-group">
        <label>Supervisor*:</label>
        <select v-model="formData.supervisor" required>
          <option :value="null">-- No Supervisor Assigned --</option>
          <option v-for="s in supervisor" :key="s.id" :value="s.id">
            {{ s.name || `Supervisor #${s.id}` }}
          </option>
        </select>
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
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'

const { get, post } = useApi()
const formData = ref({
  firstname: '', lastname: '', date_of_birth: '',
  department: null, supervisor: null, password: '', confirm_password: ''
})
const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)
const department = ref([])
const supervisor = ref([])

// ✅ computed is read-only — never assign to it
const isPasswordMatch = computed(() =>
  !formData.value.confirm_password ||
  formData.value.password === formData.value.confirm_password
)

onMounted(async () => {
  try {
  const depRes = await get('/departments/')
  if (!depRes.ok) throw new Error('Failed to fetch departments.')
  department.value = await depRes.json()
  } catch (error) {
    console.error('Error fetching departments:', error)
  }
})

const onSelectedDepartment = async () => {
  if (formData.value.department) {
    try{
    const supRes = await get(`/supervisors/?department=${formData.value.department}`)
    supervisor.value = await supRes.json()
  } catch (error) {
    console.error('Error fetching supervisors:', error)
  }
  } else {
    supervisor.value = []
  }
}

const handleRegister = async () => {
  if (formData.value.password !== formData.value.confirm_password) {
    submitError.value = 'Passwords do not match.'
    return
  }
  isSubmitting.value = true
  submitError.value = ''
  try {
    // ✅ Strip confirm_password before sending to backend
    const { confirm_password, ...payload } = formData.value
    const response = await post('/register_employee/', payload, false)
    const data = await response.json()
    if (!response.ok) throw new Error(data.error || 'Registration failed.')
    submitSuccess.value = true
  } catch (err) {
    submitError.value = err.message
  } finally {
    isSubmitting.value = false
  }
}
</script>