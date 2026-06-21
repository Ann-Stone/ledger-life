import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { StockPnlSummary } from '@/types/models'

vi.mock('@/api/otherAssets', () => ({
  getStockPnlSummary: vi.fn(),
}))

import { getStockPnlSummary } from '@/api/otherAssets'
import { useOtherAssetsStore } from '@/stores/otherAssets'

const SUMMARY: StockPnlSummary[] = [
  {
    stock_id: 'STK_0050',
    stock_code: '0050',
    stock_name: '元大台灣 50',
    shares: 1000,
    cost: 165000,
    market_value: 190000,
    realized: 0,
    dividends_total: 4500,
    unrealized: 25000,
    unrealized_pct: 0.1515,
    cash_yield: 0.0237,
    cost_yield: 0.0273,
    fx_code: 'TWD',
    close_price: 190,
    price_date: '20260619',
  },
]

describe('useOtherAssetsStore — stock P&L summary', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchStockPnl populates state and clears loading', async () => {
    vi.mocked(getStockPnlSummary).mockResolvedValue(SUMMARY)
    const store = useOtherAssetsStore()
    expect(store.stockPnl).toEqual([])

    await store.fetchStockPnl('STK')

    expect(getStockPnlSummary).toHaveBeenCalledWith('STK')
    expect(store.stockPnl).toEqual(SUMMARY)
    expect(store.stockPnlLoading).toBe(false)
  })
})
