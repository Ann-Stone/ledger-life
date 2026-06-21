import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { StockAllocationReport, StockCategory } from '@/types/models'

vi.mock('@/api/setting', () => ({
  getStockCategories: vi.fn(),
}))
vi.mock('@/api/yearReport', () => ({
  getStockAllocation: vi.fn(),
}))

import { getStockCategories } from '@/api/setting'
import { getStockAllocation } from '@/api/yearReport'
import { useSettingStore } from '@/stores/setting'
import { useYearReportStore } from '@/stores/yearReport'

const CATEGORIES: StockCategory[] = [
  { category_id: 'SC-001', name: '成長型', in_use: 'Y', category_index: 1 },
  { category_id: 'SC-002', name: '債券', in_use: 'N', category_index: 2 },
]

const ALLOCATION: StockAllocationReport = {
  total: 1000,
  items: [
    { category_id: 'SC-001', category_name: '成長型', amount: 700, share: 70 },
    { category_id: null, category_name: '未分類', amount: 300, share: 30 },
  ],
}

describe('useSettingStore — stock categories', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchStockCategories populates state and clears loading', async () => {
    vi.mocked(getStockCategories).mockResolvedValue(CATEGORIES)
    const store = useSettingStore()
    expect(store.stockCategories).toEqual([])

    await store.fetchStockCategories()

    expect(getStockCategories).toHaveBeenCalledOnce()
    expect(store.stockCategories).toEqual(CATEGORIES)
    expect(store.stockCategoriesLoading).toBe(false)
  })
})

describe('useYearReportStore — stock allocation', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchStockAllocation populates state and clears loading', async () => {
    vi.mocked(getStockAllocation).mockResolvedValue(ALLOCATION)
    const store = useYearReportStore()
    expect(store.stockAllocation).toBeNull()

    await store.fetchStockAllocation()

    expect(getStockAllocation).toHaveBeenCalledOnce()
    expect(store.stockAllocation).toEqual(ALLOCATION)
    expect(store.stockAllocationLoading).toBe(false)
  })
})
