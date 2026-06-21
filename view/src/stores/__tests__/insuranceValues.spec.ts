import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import type { InsuranceValueMonth } from '@/types/models'

vi.mock('@/api/cashFlow', () => ({
  getInsuranceValues: vi.fn(),
}))

import { getInsuranceValues } from '@/api/cashFlow'
import { useCashFlowStore } from '@/stores/cashFlow'

const VALUES: InsuranceValueMonth[] = [
  {
    insurance_id: 'INS-001',
    insurance_name: '富邦人壽終身壽險',
    surrender_value: null,
    vesting_month: null,
    recorded: false,
  },
  {
    insurance_id: 'INS-002',
    insurance_name: '南山儲蓄險',
    surrender_value: 312000,
    vesting_month: '202604',
    recorded: false,
  },
]

describe('useCashFlowStore — insurance surrender values', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    vi.clearAllMocks()
  })

  it('fetchInsuranceValues populates state and clears loading', async () => {
    vi.mocked(getInsuranceValues).mockResolvedValue(VALUES)
    const store = useCashFlowStore()
    expect(store.insuranceValues).toEqual([])

    await store.fetchInsuranceValues('202605')

    expect(getInsuranceValues).toHaveBeenCalledWith('202605')
    expect(store.insuranceValues).toEqual(VALUES)
    expect(store.insuranceValuesLoading).toBe(false)
  })

  it('defaults the month to selectedMonth', async () => {
    vi.mocked(getInsuranceValues).mockResolvedValue([])
    const store = useCashFlowStore()
    store.selectedMonth = '202601'

    await store.fetchInsuranceValues()

    expect(getInsuranceValues).toHaveBeenCalledWith('202601')
  })
})
