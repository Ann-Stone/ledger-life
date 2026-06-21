/**
 * System-defined financial behaviors used as `action_main` in Journal rows
 * when `action_main_table` is not a code table.
 *
 * Equivalent to the legacy frontend constant `financialBehavior` — these are
 * built-in semantics (transfer, repayment, etc.) wired into settle/month-end
 * logic, not data the user manages from the UI.
 *
 * Legacy data uses inconsistent table naming (`CreditCard` vs `Credit_Card`),
 * so the lookup tolerates either form.
 */
import { i18n } from '@/i18n'

export interface FinancialBehavior {
  key: string
  table: string
  labelKey: string
}

export const FINANCIAL_BEHAVIORS: FinancialBehavior[] = [
  { key: 'Transfer', table: 'Account', labelKey: 'financialBehavior.transfer' },
  { key: 'CreditCardRepayment', table: 'Credit_Card', labelKey: 'financialBehavior.creditCardRepayment' },
  { key: 'LoanRepayment', table: 'Loan', labelKey: 'financialBehavior.loanRepayment' },
  { key: 'Premiums', table: 'Insurance', labelKey: 'financialBehavior.premiums' },
]

function normalizeTable(table?: string | null): string {
  return (table ?? '').replace(/_/g, '').toLowerCase()
}

export function getFinancialBehaviorLabel(
  key?: string | null,
  table?: string | null,
): string | undefined {
  if (!key) return undefined
  const t = normalizeTable(table)
  const behavior = FINANCIAL_BEHAVIORS.find(
    (b) => b.key === key && normalizeTable(b.table) === t,
  )
  return behavior ? i18n.global.t(behavior.labelKey) : undefined
}
