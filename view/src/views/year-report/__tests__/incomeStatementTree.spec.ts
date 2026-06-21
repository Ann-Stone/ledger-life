import { describe, it, expect } from 'vitest'
import { buildIncomeStatementTree } from '../incomeStatementTree'
import type { IncomeStatementSummary } from '@/types/models'

const t = (key: string) => key

const summary: IncomeStatementSummary = {
  active_income: 100_000,
  fixed: 30_000,
  floating: 20_000,
  loan_interest: 6_000,
  operating_net: 44_000,
  dividend: 5_000,
  realized: 8_000,
  unrealized: -3_000,
  investment_net: 10_000,
  comprehensive_net: 54_000,
}

describe('buildIncomeStatementTree', () => {
  it('builds 本業 / 投資 / 綜合 sections in order', () => {
    const tree = buildIncomeStatementTree(summary, t)
    expect(tree.map((n) => n.key)).toEqual(['operating', 'investment', 'comprehensive'])
    expect(tree[0].children?.map((c) => c.key)).toEqual(['active', 'fixed', 'floating', 'loanInterest'])
    expect(tree[1].children?.map((c) => c.key)).toEqual(['dividend', 'realized', 'unrealized'])
    expect(tree[2].children).toBeUndefined()
  })

  it('negates fixed/floating/loan-interest expense magnitudes into outflows', () => {
    const tree = buildIncomeStatementTree(summary, t)
    const operating = tree[0].children!
    expect(operating.find((c) => c.key === 'fixed')!.amount).toBe(-30_000)
    expect(operating.find((c) => c.key === 'floating')!.amount).toBe(-20_000)
    expect(operating.find((c) => c.key === 'loanInterest')!.amount).toBe(-6_000)
    expect(operating.find((c) => c.key === 'active')!.amount).toBe(100_000)
  })

  it('passes signed investment figures through unchanged', () => {
    const investment = buildIncomeStatementTree(summary, t)[1].children!
    expect(investment.find((c) => c.key === 'unrealized')!.amount).toBe(-3_000)
    expect(buildIncomeStatementTree(summary, t)[2].amount).toBe(54_000)
  })
})
