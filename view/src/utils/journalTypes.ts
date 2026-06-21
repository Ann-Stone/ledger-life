/**
 * Journal `action_main_type` buckets — frontend mirror of
 * `api/app/services/journal_types.py` (`KNOWN_MAIN_TYPES` / `is_uncategorized`).
 * Keep the two in sync: the reports bucket by these exact normalized values,
 * so "uncategorized" here must mean "invisible to the reports" there.
 */
export const KNOWN_MAIN_TYPES: ReadonlySet<string> = new Set([
  'fixed',
  'floating',
  'income',
  'passive',
  'invest',
  'transfer',
  // Loan repayment (財務行為「繳貸款」) — report-neutral like transfer; the
  // principal/interest split is sourced from Loan_Journal, so it must not be
  // flagged uncategorized. Keep in sync with FINANCING_MAIN_TYPES (backend).
  'loanrepayment',
])

export function normType(actionMainType?: string | null): string {
  return (actionMainType ?? '').trim().toLowerCase()
}

/** True when the type falls outside every report bucket (e.g. legacy 'undefined'/'No'/''). */
export function isUncategorized(actionMainType?: string | null): boolean {
  return !KNOWN_MAIN_TYPES.has(normType(actionMainType))
}
