import { describe, it, expect, vi } from 'vitest'
import { nextTick } from 'vue'
import { useMonthDatePicker } from '@/composables/useMonthDatePicker'

describe('useMonthDatePicker', () => {
  it('initializes from the current YYYYMM', () => {
    const { selectedMonthDate } = useMonthDatePicker({
      current: () => '202604',
      onChange: vi.fn(),
    })
    expect(selectedMonthDate.value.getFullYear()).toBe(2026)
    expect(selectedMonthDate.value.getMonth()).toBe(3)
  })

  it('fires onChange with the new YYYYMM when a different month is picked', async () => {
    const onChange = vi.fn()
    const { selectedMonthDate } = useMonthDatePicker({ current: () => '202604', onChange })
    selectedMonthDate.value = new Date(2025, 11, 15)
    await nextTick()
    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onChange).toHaveBeenCalledWith('202512')
  })

  it('does not fire onChange when the same month is re-picked', async () => {
    const onChange = vi.fn()
    const { selectedMonthDate } = useMonthDatePicker({ current: () => '202604', onChange })
    selectedMonthDate.value = new Date(2026, 3, 20)
    await nextTick()
    expect(onChange).not.toHaveBeenCalled()
  })

  it('ignores a cleared (null) date', async () => {
    const onChange = vi.fn()
    const { selectedMonthDate } = useMonthDatePicker({ current: () => '202604', onChange })
    selectedMonthDate.value = null as unknown as Date
    await nextTick()
    expect(onChange).not.toHaveBeenCalled()
  })
})
