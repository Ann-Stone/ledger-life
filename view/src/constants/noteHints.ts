/**
 * Per-category placeholder hints for the journal `note` field.
 *
 * Matching:
 *  - For financial behaviors, set `main` to the behavior key (e.g., 'Transfer').
 *  - For codes, set `main` (and optionally `sub`) to the *display name*. Names
 *    survive ID changes from re-imports better than code_ids, and the user
 *    sees them when editing the form. These display-name matchers are backend
 *    data, NOT UI language, so they stay as-is; only the placeholder is localized.
 *
 * Resolution order:
 *   1. exact (main, sub) match
 *   2. main-only match (applies to any sub under this main)
 *   3. fallback to noteHints.optional
 */
import { i18n } from '@/i18n'

export interface NoteHint {
  main: string
  sub?: string
  key: string
}

const NOTE_HINT_FALLBACK = 'noteHints.optional'

export const NOTE_HINTS: NoteHint[] = [
  // ─── Financial behaviors ─────────────────────────────────────────────────
  { main: 'Transfer', key: 'noteHints.transfer' },
  { main: 'CreditCardRepayment', key: 'noteHints.creditCardRepayment' },
  { main: 'LoanRepayment', key: 'noteHints.loanRepayment' },
  { main: 'Premiums', key: 'noteHints.premiums' },

  // ─── 借出 / 借入 ──────────────────────────────────────────────────────────
  { main: '人情往來', sub: '借出', key: 'noteHints.favorLendOut' },
  { main: '人情往來', sub: '借入', key: 'noteHints.favorBorrowIn' },
  { main: '借貸收入', sub: '借款收入', key: 'noteHints.loanIncomeBorrow' },

  // ─── 人情往來其他子分類 ───────────────────────────────────────────────────
  { main: '人情往來', sub: '婚宴', key: 'noteHints.favorWedding' },
  { main: '人情往來', sub: '送禮', key: 'noteHints.favorGift' },
  { main: '人情往來', sub: '請客', key: 'noteHints.favorTreat' },
  { main: '人情往來', key: 'noteHints.favorDefault' },

  // ─── 投資與孳息 ───────────────────────────────────────────────────────────
  { main: '孳息收入', sub: '股息', key: 'noteHints.dividendStock' },
  { main: '孳息收入', sub: '銀行利息', key: 'noteHints.dividendBankInterest' },
  { main: '孳息收入', sub: '儲蓄險配息', key: 'noteHints.dividendSavingsInsurance' },
  { main: '投資', sub: '資本利得', key: 'noteHints.investCapitalGain' },
  { main: '投資', sub: '期貨', key: 'noteHints.investFutures' },
  { main: '投資', key: 'noteHints.investDefault' },

  // ─── 信用卡紅利 ───────────────────────────────────────────────────────────
  { main: '信用卡紅利', key: 'noteHints.creditCardBonus' },

  // ─── 房租 ─────────────────────────────────────────────────────────────────
  { main: '借貸收入', sub: '房租收入', key: 'noteHints.rentIncome' },
]

function resolveNoteHintKey(main?: string | null, sub?: string | null): string {
  if (!main) return NOTE_HINT_FALLBACK
  if (sub) {
    const exact = NOTE_HINTS.find((h) => h.main === main && h.sub === sub)
    if (exact) return exact.key
  }
  const mainOnly = NOTE_HINTS.find((h) => h.main === main && !h.sub)
  if (mainOnly) return mainOnly.key
  return NOTE_HINT_FALLBACK
}

export function getNotePlaceholder(main?: string | null, sub?: string | null): string {
  return i18n.global.t(resolveNoteHintKey(main, sub))
}
