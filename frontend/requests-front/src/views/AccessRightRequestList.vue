<template>
  <div class="page">
    <div class="page-header">
      <h1>{{ t('accessRequests.listTitle') }}</h1>
      <router-link to="/access-right-requests" class="btn-primary"> + New Request </router-link>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="state-box">
      <span class="spinner" />
      {{ t('accessRequests.loading') }}
    </div>

    <!-- Error -->
    <div v-else-if="error" class="feedback error">{{ error }}</div>

    <!-- Empty -->
    <div v-else-if="requests.length === 0" class="state-box empty">
      <p>{{ t('accessRequests.noAccessRequests') }}.</p>
      <router-link to="/access-right-requests" class="btn-primary">
        {{ t('accessRequests.createFirst') }}
      </router-link>
    </div>

    <!-- List -->
    <ul v-else class="request-list">
      <li v-for="req in requests" :key="req.id" class="request-card">
                <!-- Confirmation overlay — covers the right half of the card -->
        <Transition name="confirm">
          <div v-if="confirmingId === req.id" class="confirm-overlay">
            <p class="confirm-question">{{ t('accessRequests.confirmQuestion') }}</p>
            <div class="confirm-actions">
              <button
                class="btn-confirm-yes"
                :disabled="approvingId === req.id"
                @click="approve(req)"
              >
                {{ approvingId === req.id ? t('accessRequests.approving') : t('accessRequests.confirmYes') }}
              </button>
              <button class="btn-confirm-no" @click="confirmingId = null">
                {{ t('accessRequests.confirmNo') }}
              </button>
            </div>
          </div>
        </Transition>

        <div class="request-card-header">
          <div class="request-meta">
            <span class="zone-name">{{ req.zone_name }}</span>
            <span :class="['status-badge', req.approved ? 'approved' : 'pending']">
              {{ req.approved ? t('accessRequests.approved') : t('accessRequests.pending') }}
            </span>
          </div>
          <!-- Approve button: only visible to staff, only on pending requests -->
          <button
            v-if="auth.is_supervisor && !req.approved"
            class="btn-approve"
            :disabled="approvingId === req.id"
            @click="confirmingId = req.id"
          >
            {{
              approvingId === req.id ? t('accessRequests.approving') : t('accessRequests.approve')
            }}
          </button>
        </div>

        <div class="request-card-body">
          <div class="detail-row">
            <span class="label">{{ t('accessRequests.employee') }}</span>
            <span>{{ req.employee_name }}</span>
          </div>
          <div class="detail-row" v-if="req.supervisor_name">
            <span class="label">{{ t('accessRequests.supervisor') }}</span>
            <span>{{ req.supervisor_name }}</span>
          </div>
          <div class="detail-row">
            <span class="label">{{ t('accessRequests.period') }}</span>
            <span>{{ d(req.start_date, 'short') }} → {{ d(req.end_date, 'short') }}</span>
          </div>
          <div class="detail-row">
            <span class="label">{{ t('accessRequests.submitted') }}</span>
            <span>{{ d(req.created_at, 'short') }}</span>
          </div>
        </div>

        <p v-if="approveError[req.id]" class="feedback error">
          {{ approveError[req.id] }}
        </p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useAuthStore } from '../stores/auth'
import { useRequestCounterStore } from '@/stores/requestCounter'
import { useI18n } from 'vue-i18n'

const { get, post } = useApi()
const auth = useAuthStore()
const requestCounter = useRequestCounterStore()
const requests = ref([])
const isLoading = ref(true)
const error = ref('')
const approvingId = ref(null) // tracks which row is mid-request
const confirmingId = ref(null)
const approveError = ref({}) // per-row error messages
const { t, d } = useI18n()

onMounted(async () => {
  try {
    const res = await get('/access-right-requests/')
    if (!res.ok) throw new Error('Failed to load requests.')
    requests.value = await res.json()
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
})

const approve = async (req) => {
  approvingId.value = req.id
  requestCounter.decrement()
  confirmingId.value = null
  delete approveError.value[req.id]

  try {
    const res = await post(`/access-right-requests/${req.id}/approve/`, {})
    if (!res.ok) {
      const data = await res.json()
      throw new Error(data.error || 'Approval failed.')
    }
    // Optimistically update the row — no full refetch needed
    req.approved = true
  } catch (err) {
    approveError.value[req.id] = err.message
  } finally {
    approvingId.value = null
  }
}

const formatDate = (dateStr) =>
  new Date(dateStr).toLocaleDateString('en-GB', {
    day: '2-digit',
    month: 'short',
    year: 'numeric',
  })
</script>

<style scoped>
.page {
  max-width: 760px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}
.page-header h1 {
  font-size: 1.4rem;
  font-weight: 700;
}

.btn-primary {
  padding: 8px 16px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.875rem;
  font-weight: 600;
  cursor: pointer;
  text-decoration: none;
  transition: background 0.15s;
}
.btn-primary:hover {
  background: var(--color-primary-hover);
}

/* State boxes */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  padding: 60px 20px;
  color: var(--color-text-muted);
  text-align: center;
}

/* List */
.request-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 12px;
}
/* Card — must be relative so the overlay can position inside it */
.request-card {
  position: relative;
  overflow: hidden;             /* clips the overlay to the card's rounded corners */
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 16px 20px;
  box-shadow: var(--shadow-sm);
}

/* ── Confirmation overlay ───────────────────────────────── */
.confirm-overlay {
  position: absolute;
  top: 0;
  right: 0;           /* anchored to the right half */
  width: 55%;
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 12px;
  padding: 16px;
  background: color-mix(in oklab, var(--color-surface) 92%, var(--color-primary));
  border-inline-start: 1px solid var(--color-border);
  backdrop-filter: blur(4px);
  z-index: 10;
}

.confirm-question {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  text-align: center;
}

.confirm-actions {
  display: flex;
  gap: 8px;
}

.btn-confirm-yes {
  padding: 6px 14px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
}
.btn-confirm-yes:hover:not(:disabled) { background: var(--color-primary-hover); }
.btn-confirm-yes:disabled { opacity: 0.5; cursor: not-allowed; }

.btn-confirm-no {
  padding: 6px 14px;
  background: none;
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.8rem;
  font-weight: 500;
  cursor: pointer;
}
.btn-confirm-no:hover {
  color: var(--color-text);
  border-color: color-mix(in oklab, var(--color-text) 30%, transparent);
}

/* Slide in from the right */
.confirm-enter-active,
.confirm-leave-active {
  transition: transform 0.2s cubic-bezier(0.16, 1, 0.3, 1),
              opacity 0.2s ease;
}
.confirm-enter-from,
.confirm-leave-to {
  transform: translateX(100%);
  opacity: 0;
}


.request-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius);
  padding: 16px 20px;
  box-shadow: var(--shadow);
}

.request-card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 14px;
}

.request-meta {
  display: flex;
  align-items: center;
  gap: 10px;
}

.zone-name {
  font-weight: 700;
  font-size: 1rem;
}

.status-badge {
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  padding: 3px 8px;
  border-radius: 99px;
}
.status-badge.approved {
  background: #dcfce7;
  color: #15803d;
}
.status-badge.pending {
  background: #fef9c3;
  color: #a16207;
}

.btn-approve {
  padding: 6px 14px;
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 0.8rem;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s;
}
.btn-approve:hover:not(:disabled) {
  background: var(--color-primary-hover);
}
.btn-approve:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

/* Details */
.request-card-body {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-row {
  display: flex;
  gap: 12px;
  font-size: 0.875rem;
}
.label {
  width: 90px;
  flex-shrink: 0;
  color: var(--color-text-muted);
  font-weight: 500;
}

.feedback.error {
  margin-top: 8px;
  font-size: 0.8rem;
  color: var(--color-error);
}

/* Loading spinner */
.spinner {
  width: 24px;
  height: 24px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
}
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
