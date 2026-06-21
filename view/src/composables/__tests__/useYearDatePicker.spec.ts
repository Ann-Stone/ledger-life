import { describe, it, expect, vi } from 'vitest'
import { nextTick } from 'vue'
import { useYearDatePicker } from '@/composables/useYearDatePicker'

describe('useYearDatePicker', () => {
  it('initializes from the current year', () => {
    const { selectedYearDate } = useYearDatePicker({
      current: () => 2026,
      onChange: vi.fn(),
    })
    expect(selectedYearDate.value.getFullYear()).toBe(2026)
    expect(selectedYearDate.value.getMonth()).toBe(0)
  })

  it('fires onChange with the new year when a different year is picked', async () => {
    const onChange = vi.fn()
    const { selectedYearDate } = useYearDatePicker({ current: () => 2026, onChange })
    selectedYearDate.value = new Date(2024, 5, 10)
    await nextTick()
    expect(onChange).toHaveBeenCalledTimes(1)
    expect(onChange).toHaveBeenCalledWith(2024)
  })

  it('does not fire onChange when the same year is re-picked', async () => {
    const onChange = vi.fn()
    const { selectedYearDate } = useYearDatePicker({ current: () => 2026, onChange })
    selectedYearDate.value = new Date(2026, 11, 31)
    await nextTick()
    expect(onChange).not.toHaveBeenCalled()
  })

  it('ignores a cleared (null) date', async () => {
    const onChange = vi.fn()
    const { selectedYearDate } = useYearDatePicker({ current: () => 2026, onChange })
    selectedYearDate.value = null as unknown as Date
    await nextTick()
    expect(onChange).not.toHaveBeenCalled()
  })
})
