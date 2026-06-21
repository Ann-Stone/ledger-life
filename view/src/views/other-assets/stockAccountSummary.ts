import type { StockJournal } from '@/types/models'

export interface AccountSummary {
  account: string
  shares: number
  cost: number
  avgPrice: number | null
}

const EPS = 1e-9

/**
 * Per-account holding summary for one stock holding.
 *
 * Mirrors the moving-average cost loop in
 * `api/app/services/stock_service.py:compute_stock_pnl_summary` — but scoped to
 * each settling account's own rows, and emitting only the simplified
 * shares / cost / average-price triple the UI needs (no unrealized / yields).
 * `abs()` magnitudes keep it correct regardless of which write path produced the
 * row (asset-manage and cashflow-sync disagree on the sign of amount), and
 * `excute_price` is the whole-transaction cash amount (fees included), so
 * `avgPrice = cost / shares` is the fee-inclusive average price per share.
 *
 * Note: moving-average is path-dependent, so per-account costs need not sum to
 * the holding-level cost when the same stock is bought/sold across different
 * accounts — that is inherent to per-account accounting, not a bug.
 */
export function computeAccountSummaries(rows: StockJournal[]): AccountSummary[] {
  const byAccount = new Map<string, StockJournal[]>()
  for (const r of rows) {
    const key = r.account_name || r.account_id || ''
    const list = byAccount.get(key)
    if (list) list.push(r)
    else byAccount.set(key, [r])
  }

  const out: AccountSummary[] = []
  for (const [account, list] of byAccount) {
    const sorted = [...list].sort(
      (a, b) =>
        a.excute_date.localeCompare(b.excute_date) || a.distinct_number - b.distinct_number,
    )
    let shares = 0
    let cost = 0
    for (const r of sorted) {
      const amt = Math.abs(r.excute_amount)
      const total = Math.abs(r.excute_price) // whole-transaction amount, fees included
      if (r.excute_type === 'buy') {
        shares += amt
        cost += total
      } else if (r.excute_type === 'stock') {
        shares += amt // stock dividend / split: shares up, cost flat
      } else if (r.excute_type === 'sell') {
        const avg = shares > EPS ? cost / shares : 0
        cost -= avg * amt // remove the average cost of the shares sold
        shares -= amt
      }
      // 'cash' dividend: no effect on shares / cost
    }
    if (Math.abs(shares) < EPS) {
      shares = 0
      cost = 0
    }
    out.push({
      account,
      shares: Number(shares.toFixed(6)),
      cost: Number(cost.toFixed(2)),
      avgPrice: shares > EPS ? cost / shares : null,
    })
  }

  out.sort((a, b) => a.account.localeCompare(b.account))
  return out
}
