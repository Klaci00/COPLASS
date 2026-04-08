<template>
  <div class="register-page">
    <section class="register-card">
      <div class="register-header">
        <p class="eyebrow">AccessControl</p>
        <h1>{{ t('register.title') }}</h1>
        <p class="register-subtitle">
          {{ t('register.subtitle') }}
        </p>
      </div>

      <form class="register-form" @submit.prevent="handleRegister">
        <div class="form-grid">
          <div class="form-group">
            <label for="firstname">{{ t('register.first_name') }}</label>
            <input id="firstname" v-model="formData.firstname" type="text" required />
          </div>

          <div class="form-group">
            <label for="lastname">{{ t('register.last_name') }}</label>
            <input id="lastname" v-model="formData.lastname" type="text" required />
          </div>

          <div class="form-group">
            <label for="date_of_birth">{{ t('register.date_of_birth') }}</label>
            <input id="date_of_birth" v-model="formData.date_of_birth" type="date" required />
          </div>

          <div class="form-group">
            <label for="department">{{ t('register.department') }}</label>
            <select
              id="department"
              v-model="formData.department"
              required
              @change="onSelectedDepartment"
            >
              <option :value="null">{{ t('register.nodept') }}</option>
              <option v-for="d in department" :key="d.id" :value="d.id">
                {{ d.name || `Department #${d.id}` }}
              </option>
            </select>
          </div>

          <div class="form-group">
            <label for="supervisor">{{ t('register.supervisor') }}</label>
            <select id="supervisor" v-model="formData.supervisor" required>
              <option :value="null">{{ t('register.nosup') }}</option>
              <option v-for="s in supervisor" :key="s.id" :value="s.id">
                {{ s.name || `Supervisor #${s.id}` }}
              </option>
            </select>
          </div>

          <div class="form-group form-group-full">
            <label for="password">{{ t('register.password') }}</label>
            <input id="password" v-model="formData.password" type="password" required />
          </div>

          <div class="form-group form-group-full">
            <label for="confirm_password">{{ t('register.confirm_password') }}</label>
            <input
              id="confirm_password"
              v-model="formData.confirm_password"
              type="password"
              required
              :class="{ invalid: formData.confirm_password && !isPasswordMatch }"
            />
            <p v-if="formData.confirm_password && !isPasswordMatch" class="field-hint error-text">
              {{ t('register.password_mismatch') }}
            </p>
          </div>
        </div>

        <div v-if="submitError" class="feedback error">
          {{ submitError }}
        </div>

        <div v-if="submitSuccess" class="feedback success">
          <p>{{ t('register.success') }}</p>
          <router-link to="/login">{{ t('register.loginhere') }}</router-link>
        </div>

        <div class="form-actions">
          <button
            type="submit"
            class="btn-submit"
            :disabled="isSubmitting || !isPasswordMatch || submitSuccess"
          >
            {{ isSubmitting ? t('register.registering') : t('register.register') }}
          </button>
        </div>
      </form>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useI18n } from 'vue-i18n'

const { t } = useI18n()
const { get, post } = useApi()

const formData = ref({
  firstname: '',
  lastname: '',
  date_of_birth: '',
  department: null,
  supervisor: null,
  password: '',
  confirm_password: '',
})

const isSubmitting = ref(false)
const submitError = ref('')
const submitSuccess = ref(false)
const department = ref([])
const supervisor = ref([])

const isPasswordMatch = computed(
  () =>
    !formData.value.confirm_password || formData.value.password === formData.value.confirm_password,
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
  formData.value.supervisor = null

  if (formData.value.department) {
    try {
      const supRes = await get(`/supervisors/?department=${formData.value.department}`)
      if (!supRes.ok) throw new Error('Failed to fetch supervisors.')
      supervisor.value = await supRes.json()
    } catch (error) {
      console.error('Error fetching supervisors:', error)
      supervisor.value = []
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
    const { ...payload } = formData.value
    const response = await post('/register-employee/', payload, false)
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

<style scoped>
.register-page {
  min-height: calc(100dvh - 140px);
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px 16px;
}

.register-card {
  width: 100%;
  max-width: 760px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
  padding: 32px;
}

.register-header {
  margin-bottom: 28px;
}

.eyebrow {
  font-size: 0.75rem;
  font-weight: 700;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--color-primary);
  margin-bottom: 8px;
}

.register-header h1 {
  font-size: 1.75rem;
  line-height: 1.15;
  color: var(--color-text);
  margin-bottom: 10px;
}

.register-subtitle {
  color: var(--color-text-muted);
  max-width: 58ch;
}

.register-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-grid {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 18px 16px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group-full {
  grid-column: 1 / -1;
}

.form-group label {
  font-size: 0.88rem;
  font-weight: 600;
  color: var(--color-text);
}

.form-group input,
.form-group select {
  width: 100%;
  min-height: 44px;
  padding: 10px 12px;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  color: var(--color-text);
  font-size: 0.95rem;
  outline: none;
}

.form-group input::placeholder {
  color: var(--color-text-faint);
}

.form-group input:focus,
.form-group select:focus {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px color-mix(in oklab, var(--color-primary) 14%, transparent);
}

.form-group input.invalid {
  border-color: var(--color-error);
}

.field-hint {
  font-size: 0.8rem;
  margin-top: 2px;
}

.error-text {
  color: var(--color-error);
}

.feedback {
  border-radius: var(--radius-md);
  padding: 12px 14px;
  font-size: 0.92rem;
}

.feedback.error {
  background: color-mix(in oklab, var(--color-error) 10%, transparent);
  color: var(--color-error);
  border: 1px solid color-mix(in oklab, var(--color-error) 22%, transparent);
}

.feedback.success {
  background: color-mix(in oklab, var(--color-success) 10%, transparent);
  color: var(--color-success);
  border: 1px solid color-mix(in oklab, var(--color-success) 22%, transparent);
}

.feedback.success a {
  color: var(--color-primary);
  font-weight: 600;
  text-decoration: none;
}

.feedback.success a:hover {
  text-decoration: underline;
}

.form-actions {
  display: flex;
  justify-content: flex-end;
}

.btn-submit {
  min-width: 180px;
  min-height: 44px;
  padding: 10px 16px;
  border: none;
  border-radius: var(--radius-md);
  background: var(--color-primary);
  color: white;
  font-size: 0.95rem;
  font-weight: 700;
  cursor: pointer;
}

.btn-submit:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-submit:disabled {
  opacity: 0.55;
  cursor: not-allowed;
}

@media (max-width: 720px) {
  .register-card {
    padding: 24px 18px;
  }

  .form-grid {
    grid-template-columns: 1fr;
  }

  .form-group-full {
    grid-column: auto;
  }

  .form-actions {
    justify-content: stretch;
  }

  .btn-submit {
    width: 100%;
  }
}
</style>
