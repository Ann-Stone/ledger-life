import { createI18n } from 'vue-i18n'
import zhTW from './locales/zh-TW'
import en from './locales/en'
import { numberFormats } from './formats'

export type AppLocale = 'zh-TW' | 'en'
export const SUPPORTED_LOCALES: AppLocale[] = ['zh-TW', 'en']
export const DEFAULT_LOCALE: AppLocale = 'zh-TW'
export const LOCALE_STORAGE_KEY = 'networth-locale'

/** Resolve the initial locale from localStorage (fallback zh-TW) so first paint is correct. */
export function readStoredLocale(): AppLocale {
  if (typeof window === 'undefined') return DEFAULT_LOCALE
  const saved = window.localStorage.getItem(LOCALE_STORAGE_KEY)
  return saved === 'en' || saved === 'zh-TW' ? saved : DEFAULT_LOCALE
}

export const i18n = createI18n({
  legacy: false, // Composition API mode (useI18n)
  globalInjection: true, // expose $t / $n in templates
  locale: readStoredLocale(),
  fallbackLocale: DEFAULT_LOCALE,
  messages: { 'zh-TW': zhTW, en },
  numberFormats,
  missingWarn: import.meta.env.DEV,
  fallbackWarn: import.meta.env.DEV,
})
