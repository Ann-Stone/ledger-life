import { describe, it, expect } from 'vitest'
import { computeStockPnlSummary } from '@/api/mock/handlers/assets'

// Verifies the mock's per-stock P&L mirrors the backend accounting for the seed
// transactions. excute_price is the whole-transaction amount (fees included),
// not a per-share price; close prices (190/1100/530) are per-share market quotes.
describe('mock computeStockPnlSummary', () => {
  it('TWD holding with a cash dividend (0050)', () => {
    const s = computeStockPnlSummary('STK').find((r) => r.stock_id === 'STK_0050')!
    expect(s.fx_code).toBe('TWD')
    expect(s.shares).toBe(1000)
    expect(s.cost).toBe(165000) // buy total
    expect(s.market_value).toBe(190000) // 1000 × 190
    expect(s.unrealized).toBe(25000)
    expect(s.realized).toBe(0)
    expect(s.dividends_total).toBe(4500) // cash dividend total
    expect(s.cost_yield).toBeCloseTo(4500 / 165000, 6)
    expect(s.cash_yield).toBeCloseTo(4500 / 190000, 6)
  })

  it('partial sell realizes net proceeds minus average cost (2330)', () => {
    const s = computeStockPnlSummary('STK').find((r) => r.stock_id === 'STK_2330')!
    expect(s.shares).toBe(40) // 50 − 10
    expect(s.cost).toBe(34000) // 42500 − 10 × avg 850
    expect(s.realized).toBe(700) // proceeds 9200 − 10 × avg 850
    expect(s.market_value).toBe(44000) // 40 × 1100
    expect(s.unrealized).toBe(10000)
  })

  it('foreign holding reports its own currency; stock dividend dilutes average (VOO)', () => {
    const s = computeStockPnlSummary('STK_US').find((r) => r.stock_id === 'STK_VOO')!
    expect(s.fx_code).toBe('USD')
    expect(s.shares).toBe(6) // 5 bought + 1 stock dividend
    expect(s.cost).toBe(2400) // buy total, dividend share adds no cost
    expect(s.market_value).toBe(3180) // 6 × 530
    expect(s.unrealized).toBe(780)
  })
})
