import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { EstateValueMonth } from '@/types/models'

vi.mock('@/api/cashFlow', () => ({
  getEstateValues: vi.fn(),
}))

import { getEstateValues } from '@/api/cashFlow'
import { useCashFlowStore } from '@/stores/cashFlow'

const VALUES: EstateValueMonth[] = [
  {
    estate_id: 'EST-001',
    estate_name: '主要住所',
    market_value: 13800000,
    vesting_month: '202604',
    recorded: false,
  },
  {
    estate_id: 'EST-002',
    estate_name: '投資宅 A',
    market_value: null,
    vesting_month: null,
    recorded: false,
  },
]

describe('useCashFlowStore — estate market values', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchEstateValues populates state and clears loading', async () => {
    vi.mocked(getEstateValues).mockResolvedValue(VALUES)
    const store = useCashFlowStore()
    expect(store.estateValues).toEqual([])

    await store.fetchEstateValues('202605')

    expect(getEstateValues).toHaveBeenCalledWith('202605')
    expect(store.estateValues).toEqual(VALUES)
    expect(store.estateValuesLoading).toBe(false)
  })

  it('defaults the month to selectedMonth', async () => {
    vi.mocked(getEstateValues).mockResolvedValue([])
    const store = useCashFlowStore()
    store.selectedMonth = '202601'

    await store.fetchEstateValues()

    expect(getEstateValues).toHaveBeenCalledWith('202601')
  })
})
