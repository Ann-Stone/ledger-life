import { ref, watch, type Ref } from 'vue'

/**
 * Year-picker Date model for report views. Initializes from the current
 * store year and calls `onChange` only when a different year is picked
 * (clearing the picker is a no-op).
 */
export function useYearDatePicker(options: {
  current: () => number
  onChange: (year: number) => void
}): { selectedYearDate: Ref<Date> } {
  const selectedYearDate = ref<Date>(new Date(options.current(), 0, 1))

  watch(selectedYearDate, (date) => {
    if (!date) return
    const year = date.getFullYear()
    if (year !== options.current()) {
      options.onChange(year)
    }
  })

  return { selectedYearDate }
}
