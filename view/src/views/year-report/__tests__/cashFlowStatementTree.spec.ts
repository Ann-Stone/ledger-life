import { describe, it, expect } from 'vitest'
import { buildCashFlowTree } from '../cashFlowStatementTree'
import type { CashFlowSummary } from '@/types/models'

const t = (key: string) => key

const summary: CashFlowSummary = {
  activities: [
    {
      key: 'operating',
      label: '生活',
      net: 40_000,
      items: [
        { label: '收入', amount: 100_000 },
        { label: '生活支出', amount: -60_000 },
      ],
    },
    { key: 'investing', label: '投資', net: -25_000, items: [{ label: '買入', amount: -25_000 }] },
  ],
  net_change: 15_000,
}

describe('buildCashFlowTree', () => {
  it('maps activities with API labels and appends net_change last', () => {
    const tree = buildCashFlowTree(summary, t)
    expect(tree.map((n) => n.key)).toEqual(['operating', 'investing', 'net_change'])
    expect(tree[0].label).toBe('生活')
    expect(tree[1].amount).toBe(-25_000)
    const last = tree[tree.length - 1]
    expect(last.label).toBe('cashFlowStatement.netChange')
    expect(last.amount).toBe(15_000)
    expect(last.children).toBeUndefined()
  })

  it('keys child items by activity and index', () => {
    const tree = buildCashFlowTree(summary, t)
    expect(tree[0].children?.map((c) => c.key)).toEqual(['operating-0', 'operating-1'])
    expect(tree[0].children?.[1].amount).toBe(-60_000)
  })
})
