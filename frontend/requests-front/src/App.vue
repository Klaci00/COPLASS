<template :key="$route.path">
  <div id="app">
    <nav class="navbar">
      <span class="navbar-brand">🔐 AccessControl</span>
      <span class="navbar-brand" v-if="auth.is_logged_in"> Welcome, {{ auth.display_name }}! </span>
      <div class="navbar-links">
        <template v-if="auth.is_logged_in">
          <router-link to="/dashboard">Dashboard</router-link>
          <router-link to="/access-right-requests">Access Requests</router-link>
          <router-link to="/access-right-requests/list">Request List<span v-if="requestCounter.unapprovedCount > 0" class="badge">{{ requestCounter.unapprovedCount }}</span></router-link>
          <router-link to="/messages">
            Messages
            <span v-if="counter.unreadCount > 0" class="badge">{{ counter.unreadCount }}</span>
          </router-link>
          <template v-if="auth.is_supervisor">
            <router-link to="/new-employees">New Employees<span v-if="newEmpCounter.unapprovedCount > 0" class="badge">{{ newEmpCounter.unapprovedCount }}</span></router-link>
          </template>
          <button class="btn-logout" @click="handleLogout">Logout</button>
        </template>
        <template v-else>
          <router-link to="/login">Login</router-link>
          <router-link to="/register">Register</router-link>
        </template>
      </div>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useRouter, useRoute } from 'vue-router'
import { watch } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRequestCounterStore } from './stores/requestCounter'
import { useMessageCounterStore } from './stores/messageCounter'
import { useNewEmpCounterStore } from './stores/newEmpCounter'
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const counter = useMessageCounterStore()
const requestCounter = useRequestCounterStore()
const newEmpCounter = useNewEmpCounterStore()
let pollInterval = null
// On route change
watch(
  () => route.path,
  () => {
    if (auth.is_logged_in) {counter.fetchUnreadCount()
                            requestCounter.fetchunapprovedCount()
                            newEmpCounter.fetchunapprovedCount()
    }
  },
)

// On login/logout (manages the interval)
watch(
  () => auth.is_logged_in,
  (loggedIn) => {
    if (loggedIn) {
      counter.fetchUnreadCount()
      requestCounter.fetchunapprovedCount()
      newEmpCounter.fetchunapprovedCount()
      pollInterval = setInterval(() => {
        counter.fetchUnreadCount()
        requestCounter.fetchunapprovedCount()
        newEmpCounter.fetchunapprovedCount()
      }, 60000) // every 60s
    } else {
      counter.reset()
      requestCounter.reset()
      newEmpCounter.reset() 
      clearInterval(pollInterval)
    }
  },
  { immediate: true },
)
// Add this once in App.vue, outside the watch
document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    intervals.forEach(clearInterval)
  } else if (auth.is_logged_in) {
    // Refetch immediately when tab becomes visible again
    counter.fetchUnreadCount()
    requestCounter.fetchunapprovedCount()
    newEmpCounter.fetchunapprovedCount()
  }
})

const handleLogout = () => {
  auth.logout()
  router.push('/login')
}
</script>
<style>
:root {
  --color-bg: #f5f5f7;
  --color-surface: #ffffff;
  --color-border: #e0e0e0;
  --color-text: #1a1a2e;
  --color-text-muted: #6b7280;
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-danger: #dc2626;
  --color-danger-hover: #b91c1c;
  --color-success: #16a34a;
  --color-error: #dc2626;
  --radius: 8px;
  --shadow: 0 1px 3px rgba(0, 0, 0, 0.08), 0 4px 12px rgba(0, 0, 0, 0.06);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}
body {
  font-family: 'Inter', system-ui, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
}

.navbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 32px;
  height: 60px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.06);
}

.navbar-brand {
  font-weight: 700;
  font-size: 1.1rem;
  letter-spacing: -0.01em;
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 24px;
}

.navbar-links a {
  font-size: 0.9rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  position: relative;
  transition: color 0.15s;
}
.navbar-links a:hover {
  color: var(--color-text);
}
.navbar-links a.router-link-active {
  color: var(--color-primary);
}

.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-danger);
  color: white;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: 99px;
  min-width: 16px;
  height: 16px;
  padding: 0 4px;
  margin-left: 4px;
  vertical-align: middle;
}

.btn-logout {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-danger);
  background: none;
  border: 1px solid var(--color-danger);
  border-radius: var(--radius);
  padding: 6px 14px;
  cursor: pointer;
  transition: all 0.15s;
}
.btn-logout:hover {
  background: var(--color-danger);
  color: white;
}

main {
  padding: 40px 32px;
  max-width: 960px;
  margin: 0 auto;
}
</style>
