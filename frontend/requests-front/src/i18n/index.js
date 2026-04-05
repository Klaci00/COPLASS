// src/i18n/index.js
import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import hu from './locales/hu.json'

export const i18n = createI18n({
  legacy: false, // ✅ Required for <script setup> / Composition API
  locale: localStorage.getItem('locale') || 'en',
  fallbackLocale: 'en',
  messages: { en, hu },
})
