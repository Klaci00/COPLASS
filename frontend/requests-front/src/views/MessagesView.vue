<template>
  <div class="page">
    <div class="page-header">
      <h1>Messages</h1>
      <span v-if="unreadCount > 0" class="unread-count">
        {{ unreadCount }} unread
      </span>
    </div>

    <!-- Loading -->
    <div v-if="isLoading" class="state-box">
      <span class="spinner" />
      Loading messages…
    </div>

    <!-- Error -->
    <div v-else-if="error" class="feedback error">{{ error }}</div>

    <!-- Empty -->
    <div v-else-if="messages.length === 0" class="state-box empty">
      <svg width="32" height="32" viewBox="0 0 24 24" fill="none"
           stroke="currentColor" stroke-width="1.5" stroke-linecap="round"
           stroke-linejoin="round" aria-hidden="true">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/>
      </svg>
      <p>No messages yet.</p>
    </div>

    <!-- List -->
    <TransitionGroup v-else name="fade-slide" tag="ul" class="message-list">
      <li
        v-for="msg in messages"
        :key="msg.id"
        class="message-card"
        :class="{ unread: !msg.is_read }"
        @click="markAsRead(msg)"
        :aria-label="msg.is_read ? 'Message (read)' : 'Message (unread) — click to mark as read'"
      >
        <div class="msg-header">
          <div class="msg-meta">
            <span v-if="!msg.is_read" class="unread-dot" aria-hidden="true" />
            <span class="msg-status">{{ msg.is_read ? 'Read' : 'New' }}</span>
          </div>
          <time class="msg-date" :datetime="msg.created_at">
            {{ new Date(msg.created_at).toLocaleString() }}
          </time>
        </div>
        <p class="msg-content">{{ msg.content }}</p>
      </li>
    </TransitionGroup>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useAuthStore } from '../stores/auth'
import { useMessageCounterStore } from '../stores/messageCounter'

const auth = useAuthStore()
const counter = useMessageCounterStore()
const { get, post } = useApi()

const messages = ref([])
const isLoading = ref(true)
const error = ref('')

const unreadCount = computed(() => messages.value.filter(m => !m.is_read).length)

onMounted(async () => {
  if (!auth.hr_id) {
    error.value = 'You must be logged in to view messages.'
    isLoading.value = false
    return
  }
  try {
    const response = await get(`/messages/?employee_id=${auth.hr_id}`)
    if (!response.ok) throw new Error('Failed to fetch messages.')
    messages.value = await response.json()
  } catch (err) {
    error.value = err.message
  } finally {
    isLoading.value = false
  }
})

const markAsRead = async (msg) => {
  if (msg.is_read) return
  try {
    const response = await post('/messages/', { id: msg.id, is_read: true })
    if (!response.ok) throw new Error('Failed to update message.')
    msg.is_read = true
    counter.decrement()
  } catch (err) {
    error.value = err.message
  }
}
</script>

<style scoped>
.page {
  max-width: 680px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  align-items: baseline;
  gap: 12px;
  margin-bottom: 24px;
}

.page-header h1 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text);
}

.unread-count {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-primary);
  background: color-mix(in oklab, var(--color-primary) 12%, transparent);
  padding: 2px 10px;
  border-radius: var(--radius-full);
}

/* State boxes */
.state-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  padding: 60px 20px;
  color: var(--color-text-faint);
  text-align: center;
}

.feedback.error {
  font-size: 0.875rem;
  color: var(--color-error);
  padding: 10px 14px;
  background: color-mix(in oklab, var(--color-error) 8%, transparent);
  border-radius: var(--radius-md);
}

/* List */
.message-list {
  list-style: none;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.message-card {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 14px 18px;
  cursor: pointer;
  transition:
    background-color 0.15s ease,
    box-shadow 0.15s ease,
    border-color 0.15s ease;
}

.message-card:hover {
  background: var(--color-surface-2);
  box-shadow: var(--shadow-sm);
}

/* Unread: elevated surface + accent border, NOT a colored side border */
.message-card.unread {
  background: color-mix(in oklab, var(--color-primary) 5%, var(--color-surface));
  border-color: color-mix(in oklab, var(--color-primary) 25%, transparent);
}

.msg-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.msg-meta {
  display: flex;
  align-items: center;
  gap: 7px;
}

/* Small dot indicator instead of a thick colored border */
.unread-dot {
  width: 7px;
  height: 7px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  flex-shrink: 0;
}

.msg-status {
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text-muted);
}

.unread .msg-status {
  color: var(--color-primary);
}

.msg-date {
  font-size: 0.78rem;
  color: var(--color-text-faint);
}

.msg-content {
  font-size: 0.9rem;
  color: var(--color-text);
  line-height: 1.55;
}

.unread .msg-content {
  color: var(--color-text);
  font-weight: 450;
}

/* Spinner */
.spinner {
  width: 24px;
  height: 24px;
  border: 2px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
  display: inline-block;
  flex-shrink: 0;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* Mark-as-read fade */
.fade-slide-leave-active {
  transition: all 0.25s ease;
}
.fade-slide-leave-to {
  opacity: 0;
  transform: translateX(12px);
}
</style>