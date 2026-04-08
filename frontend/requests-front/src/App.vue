<template>
  <div id="app">
    <nav class="navbar">
      <!-- Brand -->
      <router-link to="/dashboard" class="navbar-brand">
        <svg
          width="20"
          height="20"
          viewBox="0 0 24 24"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          stroke-linecap="round"
          stroke-linejoin="round"
          aria-hidden="true"
        >
          <rect x="3" y="11" width="18" height="11" rx="2" ry="2" />
          <path d="M7 11V7a5 5 0 0 1 10 0v4" />
        </svg>
        <span>AccessControl</span>
      </router-link>

      <!-- Nav links (logged in) -->
      <template v-if="auth.is_logged_in">
        <div class="navbar-links">
          <router-link to="/dashboard">{{ t('nav.dashboard') }}</router-link>
          <router-link to="/access-right-requests">{{ t('nav.accessRequests') }}</router-link>
          <router-link to="/access-right-requests/list">
            {{ t('nav.requestList') }}
            <span v-if="requestCounter.unapprovedCount > 0" class="badge">
              {{ requestCounter.unapprovedCount }}
            </span>
          </router-link>
          <router-link to="/messages">
            {{ t('nav.messages') }}
            <span v-if="counter.unreadCount > 0" class="badge">
              {{ counter.unreadCount }}
            </span>
          </router-link>
          <router-link v-if="auth.is_supervisor" to="/new-employees">
            {{ t('nav.newEmployees') }}
            <span v-if="newEmpCounter.unapprovedCount > 0" class="badge">
              {{ newEmpCounter.unapprovedCount }}
            </span>
          </router-link>
        </div>

        <!-- Right side controls -->
        <div class="navbar-actions">
          <span v-if="auth.is_supervisor" class="supervisor-badge">Supervisor</span>
          <div class="navbar-divider" aria-hidden="true" />
          <div class="user-pill">
            <span class="user-avatar" aria-hidden="true">
              {{ auth.user_name ? auth.user_name[0].toUpperCase() : '?' }}
            </span>
            <span class="user-name">{{ t('nav.logout') }}</span>
          </div>
          <div class="navbar-divider" aria-hidden="true" />
          <select class="lang-switcher" v-model="locale" @change="saveLang">
            <option value="en">EN</option>
            <option value="hu">HU</option>
            <option value="ar">AR</option>
          </select>
          <!-- Theme toggle -->
          <button
            class="btn-icon"
            @click="theme.toggle()"
            :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          >
            <!-- Sun icon -->
            <svg
              v-if="theme.isDark"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <circle cx="12" cy="12" r="5" />
              <path
                d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42
                       M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
              />
            </svg>
            <!-- Moon icon -->
            <svg
              v-else
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
              aria-hidden="true"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </button>
          <button class="btn-logout" @click="handleLogout">{{ t('nav.logout') }}</button>
        </div>
      </template>

      <!-- Guest links -->
      <template v-else>
        <div class="navbar-actions">
          <select class="lang-switcher" v-model="locale" @change="saveLang">
            <option value="en">EN</option>
            <option value="hu">HU</option>
            <option value="ar">AR</option>
          </select>

          <button
            class="btn-icon"
            @click="theme.toggle()"
            :aria-label="theme.isDark ? 'Switch to light mode' : 'Switch to dark mode'"
          >
            <svg
              v-if="theme.isDark"
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="12" cy="12" r="5" />
              <path
                d="M12 1v2M12 21v2M4.22 4.22l1.42 1.42M18.36 18.36l1.42 1.42
                       M1 12h2M21 12h2M4.22 19.78l1.42-1.42M18.36 5.64l1.42-1.42"
              />
            </svg>
            <svg
              v-else
              width="18"
              height="18"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="2"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z" />
            </svg>
          </button>
          <router-link to="/login" class="btn-outline">Login</router-link>
          <router-link to="/register" class="btn-primary-sm">Register</router-link>
        </div>
      </template>
    </nav>

    <main>
      <router-view />
    </main>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'
import { isRtl } from './i18n'
import { useRouter, useRoute } from 'vue-router'
import { watch } from 'vue'
import { useAuthStore } from './stores/auth'
import { useRequestCounterStore } from './stores/requestCounter'
import { useMessageCounterStore } from './stores/messageCounter'
import { useNewEmpCounterStore } from './stores/newEmpCounter'
import { useTheme } from './composables/theme'

const { t, locale } = useI18n()
const saveLang = () => {
  localStorage.setItem('locale', locale.value)
}
const theme = useTheme()
const auth = useAuthStore()
const router = useRouter()
const route = useRoute()
const counter = useMessageCounterStore()
const requestCounter = useRequestCounterStore()
const newEmpCounter = useNewEmpCounterStore()
let pollInterval = null

watch(
  locale,
  (newLocale) => {
    document.documentElement.setAttribute('dir', isRtl(newLocale) ? 'rtl' : 'ltr')
    document.documentElement.setAttribute('lang', newLocale)
    // In your locale watcher
    if (newLocale === 'ar') {
      const link = document.createElement('link')
      link.rel = 'stylesheet'
      link.href =
        'https://fonts.googleapis.com/css2?family=Noto+Sans+Arabic:wght@400;500;700&display=swap'
      document.head.appendChild(link)
    }
  },
  { immediate: true },
)

watch(
  () => route.path,
  () => {
    if (auth.is_logged_in) {
      counter.fetchUnreadCount()
      requestCounter.fetchunapprovedCount()
      if (auth.is_supervisor) newEmpCounter.fetchunapprovedCount()
    }
  },
)

watch(
  () => auth.is_logged_in,
  (loggedIn) => {
    if (loggedIn) {
      counter.fetchUnreadCount()
      requestCounter.fetchunapprovedCount()
      if (auth.is_supervisor) newEmpCounter.fetchunapprovedCount()

      pollInterval = setInterval(() => {
        counter.fetchUnreadCount()
        requestCounter.fetchunapprovedCount()
        if (auth.is_supervisor) newEmpCounter.fetchunapprovedCount()
      }, 60000)
    } else {
      counter.reset()
      requestCounter.reset()
      newEmpCounter.reset()
      clearInterval(pollInterval)
    }
  },
  { immediate: true },
)

document.addEventListener('visibilitychange', () => {
  if (document.hidden) {
    clearInterval(pollInterval)
  } else if (auth.is_logged_in) {
    counter.fetchUnreadCount()
    requestCounter.fetchunapprovedCount()
    if (auth.is_supervisor) newEmpCounter.fetchunapprovedCount()
  }
})

const handleLogout = () => {
  router.push('/login')
  auth.logout()
}
</script>

<style>
/* ─── Tokens ─────────────────────────────────────────────── */
:root {
  --color-bg: #f5f5f7;
  --color-surface: #ffffff;
  --color-surface-2: #f0f0f3;
  --color-border: oklch(0.2 0 0 / 0.1);
  --color-text: #111318;
  --color-text-muted: #6b7280;
  --color-text-faint: #a0a6b1;
  --color-primary: #2563eb;
  --color-primary-hover: #1d4ed8;
  --color-danger: #dc2626;
  --color-danger-hover: #b91c1c;
  --color-success: #16a34a;
  --color-error: #dc2626;
  --color-warning: #d97706;
  --radius-sm: 6px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --radius-full: 9999px;
  --shadow-sm: 0 1px 2px oklch(0.2 0 0 / 0.06);
  --shadow-md: 0 4px 12px oklch(0.2 0 0 / 0.08);
  --transition-btn: background-color 0.75s ease, border-color 0.75s ease, box-shadow 0.75s ease;
}

:root.dark {
  --color-bg: #0d0e11;
  --color-surface: #16181d;
  --color-surface-2: #1e2028;
  --color-border: oklch(1 0 0 / 0.08);
  --color-text: #e8e9ec;
  --color-text-muted: #8b909c;
  --color-text-faint: #555a66;
  --color-primary: #4d8cf5;
  --color-primary-hover: #6ba0f7;
  --color-danger: #f87171;
  --color-danger-hover: #fca5a5;
  --shadow-sm: 0 1px 2px oklch(0 0 0 / 0.3);
  --shadow-md: 0 4px 12px oklch(0 0 0 / 0.4);
}

/* ─── Reset ──────────────────────────────────────────────── */
*,
*::before,
*::after {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

html {
  -webkit-font-smoothing: antialiased;
  text-rendering: optimizeLegibility;
  scroll-behavior: smooth;
}

body {
  font-family: 'Inter', 'Noto Sans Arabic', system-ui, sans-serif;
  background: var(--color-bg);
  color: var(--color-text);
  min-height: 100dvh;
  /* ✅ Transition only color/background — not ALL properties */
  transition:
    background-color 0.2s ease,
    color 0.2s ease;
}
/*Language direction support */
.page-header {
  padding-inline-start: 24px;
  text-align: start;
}
.unread-dot {
  margin-inline-end: 7px;
}
/* Flex row direction, icon rotation, etc. */
[dir='rtl'] .navbar-links {
  flex-direction: row-reverse;
}
[dir='rtl'] .chevron-icon {
  transform: scaleX(-1);
}
/* Only interactive elements get transitions */
a,
button,
[role='button'] {
  transition:
    color 0.7s ease,
    background-color 0.15s ease,
    border-color 0.15s ease,
    box-shadow 0.15s ease,
    opacity 0.15s ease;
}

/* ─── Navbar ─────────────────────────────────────────────── */
.navbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 0 24px;
  height: 56px;
  background: color-mix(in oklab, var(--color-surface) 85%, transparent);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 100;
}

.navbar-brand {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--color-text);
  text-decoration: none;
  letter-spacing: -0.02em;
  flex-shrink: 0;
  margin-right: 8px;
}
.navbar-brand:hover {
  color: var(--color-primary);
}

.navbar-links {
  display: flex;
  align-items: center;
  gap: 2px;
  flex: 1;
  overflow-x: auto;
  scrollbar-width: none;
}
.navbar-links::-webkit-scrollbar {
  display: none;
}

.navbar-links a {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  padding: 6px 10px;
  border-radius: var(--radius-sm);
  white-space: nowrap;
  position: relative;
}
.navbar-links a:hover {
  color: var(--color-text);
  background: var(--color-surface-2);
}
.navbar-links a.router-link-active {
  color: var(--color-primary);
  background: color-mix(in oklab, var(--color-primary) 10%, transparent);
}

.navbar-actions {
  display: flex;
  align-items: center;
  gap: 8px;
  flex-shrink: 0;
  margin-left: auto;
}

.navbar-divider {
  width: 1px;
  height: 20px;
  background: var(--color-border);
  flex-shrink: 0;
}
.lang-switcher {
  font-size: 0.82rem;
  font-weight: 500;
  background: var(--color-surface-2);
  color: var(--color-text-muted);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 4px 8px;
  cursor: pointer;
  height: 34px;
}
.lang-switcher:hover {
  border-color: var(--color-primary);
}
/* Badge */
.badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  background: var(--color-danger);
  color: #fff;
  font-size: 0.65rem;
  font-weight: 700;
  border-radius: var(--radius-full);
  min-width: 15px;
  height: 15px;
  padding: 0 3px;
  margin-left: 4px;
  vertical-align: middle;
}

/* Supervisor badge */
.supervisor-badge {
  font-size: 0.7rem;
  font-weight: 600;
  color: var(--color-primary);
  background: color-mix(in oklab, var(--color-primary) 12%, transparent);
  padding: 3px 8px;
  border-radius: var(--radius-full);
  letter-spacing: 0.02em;
  text-transform: uppercase;
}

/* User pill */
.user-pill {
  display: flex;
  align-items: center;
  gap: 7px;
}

.user-avatar {
  width: 28px;
  height: 28px;
  border-radius: var(--radius-full);
  background: color-mix(in oklab, var(--color-primary) 15%, var(--color-surface-2));
  color: var(--color-primary);
  font-size: 0.75rem;
  font-weight: 700;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.user-name {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-text-muted);
  max-width: 140px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

/* Icon button (theme toggle) */
.btn-icon {
  width: 34px;
  height: 34px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  color: var(--color-text-muted);
  background: none;
  border: none;
  cursor: pointer;
  transition: var(--transition-btn);
}
.btn-icon:hover {
  color: var(--color-text);
  background: var(--color-surface-2);
}

/* Logout */
.btn-logout {
  font-size: 0.82rem;
  font-weight: 500;
  color: var(--color-danger);
  background: none;
  border: 1px solid color-mix(in oklab, var(--color-danger) 35%, transparent);
  border-radius: var(--radius-md);
  padding: 5px 12px;
  cursor: pointer;
  height: 34px;
}
.btn-logout:hover {
  background: color-mix(in oklab, var(--color-danger) 10%, transparent);
}

/* Guest buttons */
.btn-outline {
  font-size: 0.85rem;
  font-weight: 500;
  color: var(--color-text-muted);
  text-decoration: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  padding: 5px 14px;
  height: 34px;
  display: flex;
  align-items: center;
}
.btn-outline:hover {
  color: var(--color-text);
  border-color: color-mix(in oklab, var(--color-text) 30%, transparent);
}

.btn-primary-sm {
  font-size: 0.85rem;
  font-weight: 600;
  color: #fff;
  text-decoration: none;
  background: var(--color-primary);
  border-radius: var(--radius-md);
  padding: 5px 14px;
  height: 34px;
  display: flex;
  align-items: center;
}
.btn-primary-sm:hover {
  background: var(--color-primary-hover);
}

/* ─── Main content ───────────────────────────────────────── */
main {
  padding: 36px 32px;
  max-width: 980px;
  margin: 0 auto;
}
</style>
