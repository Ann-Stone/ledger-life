import { ref, watch, type Ref } from 'vue'
import { dateToYyyymm, yyyymmToDate } from '@/utils/dateFormat'

/**
 * Month-picker Date model bridging a YYYYMM store key. Calls `onChange`
 * only when a different month is picked (clearing the picker is a no-op).
 */
export function useMonthDatePicker(options: {
  current: () => string
  onChange: (yyyymm: string) => void
}): { selectedMonthDate: Ref<Date> } {
  const selectedMonthDate = ref<Date>(yyyymmToDate(options.current()))

  watch(selectedMonthDate, (date) => {
    if (!date) return
    const next = dateToYyyymm(date)
    if (next !== options.current()) {
      options.onChange(next)
    }
  })

  return { selectedMonthDate }
}
