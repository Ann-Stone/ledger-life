/**
 * Display-only translations for SelectionGroup labels.
 *
 * BE returns English keys (account_type, table names) in `SelectionGroup.label`.
 * Templates render via `translateGroupLabel(label)` to show the user-friendly
 * label in the active UI locale. Do NOT translate when storing values in journal
 * payloads — the raw key is the source of truth, only the display layer translates.
 */
import { i18n } from '@/i18n'

/** Backend SelectionGroup.label key → i18n message key (selection.*). */
const GROUP_LABEL_KEYS: Record<string, string> = {
  // Account types
  cash: 'selection.cash',
  normal: 'selection.normal',
  finance: 'selection.finance',
  eWallet: 'selection.eWallet',
  gift: 'selection.gift',
  // Other financial entities
  Credit_Card: 'selection.creditCard',
  Loan: 'selection.loan',
  Insurance: 'selection.insurance',
  Other_Asset: 'selection.otherAsset',
  // Code types (main category groups)
  Floating: 'selection.floating',
  Fixed: 'selection.fixed',
  Income: 'selection.income',
  Passive: 'selection.passive',
  Invest: 'selection.invest',
  Transfer: 'selection.transfer',
  // Component-built group header for built-in financial behaviors.
  FinancialBehavior: 'selection.financialBehaviorGroup',
}

/**
 * Translate a backend SelectionGroup label to the active UI locale.
 * Reactive in templates: `i18n.global.t` reads the global locale ref during render.
 */
export function translateGroupLabel(label: string): string {
  const key = GROUP_LABEL_KEYS[label]
  return key ? i18n.global.t(key) : label
}
