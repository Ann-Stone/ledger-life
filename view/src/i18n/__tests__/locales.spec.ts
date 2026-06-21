import { describe, it, expect } from 'vitest'
import zhTW from '@/i18n/locales/zh-TW'
import en from '@/i18n/locales/en'

/**
 * Locale parity guardrail. Flattens both message trees to dotted leaf-key paths
 * and asserts the sets are identical, so a key added to one locale but not the
 * other fails CI instead of silently falling back / showing a raw key.
 */
function leafKeys(obj: Record<string, unknown>, prefix = ''): string[] {
  return Object.entries(obj).flatMap(([k, v]) => {
    const path = prefix ? `${prefix}.${k}` : k
    return v !== null && typeof v === 'object'
      ? leafKeys(v as Record<string, unknown>, path)
      : [path]
  })
}

describe('locale parity (zh-TW ⇄ en)', () => {
  const zhKeys = leafKeys(zhTW as Record<string, unknown>).sort()
  const enKeys = leafKeys(en as Record<string, unknown>).sort()

  it('en has no missing keys vs zh-TW', () => {
    const missing = zhKeys.filter((k) => !enKeys.includes(k))
    expect(missing, `keys present in zh-TW but missing in en:\n${missing.join('\n')}`).toEqual([])
  })

  it('zh-TW has no missing keys vs en', () => {
    const extra = enKeys.filter((k) => !zhKeys.includes(k))
    expect(extra, `keys present in en but missing in zh-TW:\n${extra.join('\n')}`).toEqual([])
  })

  it('both locales define the same total number of keys', () => {
    expect(enKeys.length).toBe(zhKeys.length)
  })
})
