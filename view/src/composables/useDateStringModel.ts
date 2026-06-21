import { computed, type WritableComputedRef } from 'vue'
import { dateToYyyymmdd, yyyymmddToDate } from '@/utils/dateFormat'

/**
 * Writable Date|null model bridging a YYYYMMDD string field to el-date-picker.
 *
 * The setter receives `null` when the picker is cleared — the caller decides
 * how to store that (most fields coerce to `''`, but e.g. the loan
 * `grace_expire_date` keeps `null`).
 */
export function useDateStringModel(
  get: () => string | null | undefined,
  set: (yyyymmdd: string | null) => void,
): WritableComputedRef<Date | null> {
  return computed<Date | null>({
    get: () => yyyymmddToDate(get()),
    set: (date) => set(date ? dateToYyyymmdd(date) : null),
  })
}
