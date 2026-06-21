// Conversions between the API's date-string keys (YYYYMMDD / YYYYMM) and JS
// Date objects used by el-date-picker. Non-strict dayjs parsing on purpose —
// matches the historical inline conversions these replaced.
import dayjs from 'dayjs'

export function yyyymmddToDate(value: string | null | undefined): Date | null {
  return value ? dayjs(value, 'YYYYMMDD').toDate() : null
}

export function dateToYyyymmdd(date: Date): string {
  return dayjs(date).format('YYYYMMDD')
}

export function yyyymmToDate(value: string): Date {
  return dayjs(value, 'YYYYMM').toDate()
}

export function dateToYyyymm(date: Date): string {
  return dayjs(date).format('YYYYMM')
}

export function formatYyyymmddDisplay(value: string): string {
  return dayjs(value, 'YYYYMMDD').format('YYYY-MM-DD')
}

export function todayYyyymmdd(): string {
  return dayjs().format('YYYYMMDD')
}
