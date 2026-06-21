import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { EstateValueSuggestion, IndexRefreshResult } from '@/types/models'

vi.mock('@/api/cashFlow', () => ({
  getEstateValueSuggestions: vi.fn(),
  refreshHousePriceIndex: vi.fn(),
}))

import { getEstateValueSuggestions, refreshHousePriceIndex } from '@/api/cashFlow'
import { useCashFlowStore } from '@/stores/cashFlow'

const SUGGESTIONS: EstateValueSuggestion[] = [
  {
    estate_id: 'EST-001',
    estate_name: '主要住所',
    cost: 10000000,
    suggested_market_value: 13800000,
    region: '臺北市全市',
    obtain_quarter: '2020Q1',
    current_quarter: '2024Q1',
  },
]

describe('useCashFlowStore — house-price-index suggestions', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchEstateSuggestions populates state', async () => {
    vi.mocked(getEstateValueSuggestions).mockResolvedValue(SUGGESTIONS)
    const store = useCashFlowStore()
    store.selectedMonth = '202403'

    await store.fetchEstateSuggestions()

    expect(getEstateValueSuggestions).toHaveBeenCalledWith('202403')
    expect(store.estateSuggestions).toEqual(SUGGESTIONS)
  })

  it('refreshEstateIndex refreshes then refetches suggestions and returns the result', async () => {
    const result: IndexRefreshResult = { region: '臺北市全市', upserted: 48, ok: true }
    vi.mocked(refreshHousePriceIndex).mockResolvedValue(result)
    vi.mocked(getEstateValueSuggestions).mockResolvedValue(SUGGESTIONS)
    const store = useCashFlowStore()

    const res = await store.refreshEstateIndex()

    expect(refreshHousePriceIndex).toHaveBeenCalledOnce()
    expect(getEstateValueSuggestions).toHaveBeenCalledOnce() // refetch after refresh
    expect(res).toEqual(result)
    expect(store.estateSuggestions).toEqual(SUGGESTIONS)
  })
})
