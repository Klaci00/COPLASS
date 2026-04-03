<template>
  <div class="messages-container">
    <h2>My Messages</h2>

    <div v-if="isLoading" class="loading">Loading messages...</div>
    <div v-else-if="error" class="error">{{ error }}</div>
    <div v-else-if="messages.length === 0" class="empty">You have no messages.</div>

    <ul v-else class="message-list">
      <li
        v-for="msg in messages"
        :key="msg.id"
        :class="{ unread: !msg.is_read }"
        @click="markAsRead(msg)"
      >
        <div class="msg-header">
          <span class="status">{{ msg.is_read ? 'Read' : 'New!' }}</span>
          <span class="date">{{ new Date(msg.created_at).toLocaleString() }}</span>
        </div>
        <p class="content">{{ msg.content }}</p>
      </li>
    </ul>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useApi } from '../composables/useApi'
import { useAuthStore } from '../stores/auth'
import { useMessageCounterStore } from '../stores/messageCounter'
const auth = useAuthStore()
const counter = useMessageCounterStore()
const { get, post } = useApi()
const messages = ref([])
const isLoading = ref(true)
const error = ref('')

onMounted(async () => {
  const hrId = auth.hr_id
  if (!hrId) {
    error.value = 'You must be logged in to view messages.'
    isLoading.value = false
    return
  }
  try {
    const response = await get(`/messages/?employee_id=${hrId}`)
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
    // ✅ Pass only the data payload — the composable handles the rest
    const response = await post('/messages/', { id: msg.id, is_read: true })
    if (!response.ok) throw new Error('Failed to update message.')
    msg.is_read = true
    counter.decrement()
  } catch (err) {
    // ✅ No alert() — surface the error in the template instead
    error.value = err.message
  }
}
</script>

<style scoped>
.messages-container {
  max-width: 600px;
  margin: 20px auto;
  padding: 20px;
  background: #fdfdfd;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
}

.message-list {
  list-style-type: none;
  padding: 0;
}

.message-list li {
  background: #fff;
  border: 1px solid #eee;
  margin-bottom: 10px;
  padding: 15px;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.message-list li:hover {
  background: #f1f8ff;
  border-color: #cce5ff;
}

/* Styling for unread messages to make them pop */
.message-list li.unread {
  border-left: 5px solid #007bff;
  background: #f8fbff;
}

.msg-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
  font-size: 0.85em;
  color: #666;
}

.status {
  font-weight: bold;
}

.unread .status {
  color: #007bff;
}

.content {
  margin: 0;
  color: #333;
  line-height: 1.4;
}

.error {
  color: red;
  text-align: center;
}
.empty,
.loading {
  text-align: center;
  color: #666;
  margin-top: 20px;
}
</style>
