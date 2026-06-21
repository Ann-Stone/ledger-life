import { createI18n } from 'vue-i18n'
import zhTW from '@/i18n/locales/zh-TW'
import en from '@/i18n/locales/en'
import type { AppLocale } from '@/i18n'

/**
 * A real vue-i18n instance for component tests, configured with the actual
 * messages so `t()` returns real strings (default zh-TW keeps existing
 * Chinese assertions passing). Add to a mount's `global.plugins`.
 */
export function testI18n(locale: AppLocale = 'zh-TW') {
  return createI18n({
    legacy: false,
    locale,
    fallbackLocale: 'zh-TW',
    messages: { 'zh-TW': zhTW, en },
  })
}
