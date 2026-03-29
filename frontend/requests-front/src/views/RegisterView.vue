<script setup>
import { ref, computed } from 'vue'
import { useApi } from '../composables/useApi'

const { post } = useApi()
const formData = ref({
  firstname: '', lastname: '', date_of_birth: '',
  department: '', password: '', confirm_password: ''
})
const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)

// ✅ computed is read-only — never assign to it
const isPasswordMatch = computed(() =>
  !formData.value.confirm_password ||
  formData.value.password === formData.value.confirm_password
)

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