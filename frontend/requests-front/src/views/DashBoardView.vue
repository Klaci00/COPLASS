<template>
  <div class="dashboard">
    <h1>Dashboard</h1>
    <p>Welcome back, {{ auth.display_name }}.</p>
  </div>
</template>

<script setup>
import { useAuthStore } from '../stores/auth'

const auth = useAuthStore()
</script>

<style scoped>
.dashboard {
  padding: 32px;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-sm);
}

.dashboard h1 {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 8px;
}

.dashboard p {
  color: var(--color-text-muted);
  font-size: 0.95rem;
}
</style>