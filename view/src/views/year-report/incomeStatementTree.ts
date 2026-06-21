/**
 * Income-statement (損益表) breakdown-tree builder.
 *
 * Maps the fixed summary fields into the 本業 / 投資 / 綜合 sections the page
 * renders. `fixed` / `floating` arrive as positive expense magnitudes and are
 * NEGATED here so the tree shows them as outflows under 本業損益.
 *
 * `t` is injected so labels re-evaluate on locale switch when the caller
 * wraps the build in a `computed`.
 */
import type { IncomeStatementSummary } from '@/types/models'

export interface BreakdownNode {
  key: string
  label: string
  amount: number
  children?: BreakdownNode[]
}

export function buildIncomeStatementTree(
  summary: IncomeStatementSummary,
  t: (key: string) => string,
): BreakdownNode[] {
  return [
    {
      key: 'operating',
      label: t('incomeStatement.operatingPnl'),
      amount: summary.operating_net,
      children: [
        { key: 'active', label: t('incomeStatement.activeIncome'), amount: summary.active_income },
        { key: 'fixed', label: t('incomeStatement.fixedExpense'), amount: -summary.fixed },
        { key: 'floating', label: t('incomeStatement.floatingExpense'), amount: -summary.floating },
        { key: 'loanInterest', label: t('incomeStatement.loanInterest'), amount: -summary.loan_interest },
      ],
    },
    {
      key: 'investment',
      label: t('incomeStatement.investmentNet'),
      amount: summary.investment_net,
      children: [
        { key: 'dividend', label: t('incomeStatement.dividend'), amount: summary.dividend },
        { key: 'realized', label: t('incomeStatement.realized'), amount: summary.realized },
        { key: 'unrealized', label: t('incomeStatement.unrealized'), amount: summary.unrealized },
      ],
    },
    {
      key: 'comprehensive',
      label: t('incomeStatement.comprehensiveNet'),
      amount: summary.comprehensive_net,
    },
  ]
}
