// Locale-aware number formats for vue-i18n's `$n` / `n()` API.
// The ledger currency is always TWD regardless of UI language — only the
// grouping / symbol conventions follow the active locale.
import type { AppLocale } from './index'

type NumberFormatMap = Record<string, Intl.NumberFormatOptions>

const shared: NumberFormatMap = {
  currency: {
    style: 'currency',
    currency: 'TWD',
    currencyDisplay: 'narrowSymbol',
    minimumFractionDigits: 0,
    maximumFractionDigits: 2,
  },
  decimal: { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 2 },
  integer: { style: 'decimal', minimumFractionDigits: 0, maximumFractionDigits: 0 },
}

export const numberFormats: Record<AppLocale, NumberFormatMap> = {
  'zh-TW': shared,
  en: shared,
}
