/**
 * Cash-flow-statement (現金流量表) breakdown-tree builder.
 *
 * Activities carry API-provided labels; only the trailing 現金淨變動 row is
 * translated here, so `t` is injected for locale-reactive rebuilds inside a
 * `computed`.
 */
import type { CashFlowSummary } from '@/types/models'
import type { BreakdownNode } from './incomeStatementTree'

export function buildCashFlowTree(
  summary: CashFlowSummary,
  t: (key: string) => string,
): BreakdownNode[] {
  return [
    ...summary.activities.map((a) => ({
      key: a.key,
      label: a.label,
      amount: a.net,
      children: a.items.map((it, i) => ({
        key: `${a.key}-${i}`,
        label: it.label,
        amount: it.amount,
      })),
    })),
    { key: 'net_change', label: t('cashFlowStatement.netChange'), amount: summary.net_change },
  ]
}
