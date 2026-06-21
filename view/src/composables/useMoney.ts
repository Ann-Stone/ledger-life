import { useI18n } from 'vue-i18n'

/**
 * Locale-aware number formatting for monetary values. The grouping/locale arg
 * follows the active app locale; the currency label (e.g. `TWD`) is NOT a
 * translatable word and is handled separately by the caller.
 *
 * Call inside `setup` (it uses `useI18n`). Because `format()` reads the locale
 * ref at call time, wrapping a call in a `computed` makes it re-format on toggle.
 */
export function useMoney() {
  const { locale } = useI18n()

  function format(value: number, opts?: Intl.NumberFormatOptions): string {
    return new Intl.NumberFormat(locale.value === 'en' ? 'en-US' : 'zh-TW', {
      minimumFractionDigits: 0,
      maximumFractionDigits: 2,
      ...opts,
    }).format(value)
  }

  return { format }
}
