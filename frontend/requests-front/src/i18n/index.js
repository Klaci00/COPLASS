// src/i18n/index.js
import { createI18n } from 'vue-i18n'
import en from './locales/en.json'
import hu from './locales/hu.json'
import ar from './locales/ar.json'

const RTL_LOCALES = ['ar', 'he', 'fa', 'ur']

export const isRtl = (locale) => RTL_LOCALES.includes(locale)

export const i18n = createI18n({
  legacy: false, // ✅ Required for <script setup> / Composition API
  locale: localStorage.getItem('locale') || 'en',
  lang: localStorage.getItem('lang') || 'en',
  fallbackLocale: 'en',

  messages: { en, hu, ar },
  datetimeFormats: {
    en: {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      datetime: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      },
    },
    hu: {
      short: { year: 'numeric', month: 'long', day: 'numeric' },
      datetime: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      },
    },
    ar: {
      short: { year: 'numeric', month: 'short', day: 'numeric' },
      datetime: {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
        hour12: false,
      },
    },
  },
})
