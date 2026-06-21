import { describe, it, expect } from 'vitest'
import {
  dateToYyyymm,
  dateToYyyymmdd,
  formatYyyymmddDisplay,
  todayYyyymmdd,
  yyyymmToDate,
  yyyymmddToDate,
} from '@/utils/dateFormat'

describe('dateFormat', () => {
  it('round-trips YYYYMMDD through Date', () => {
    const date = yyyymmddToDate('20260415')
    expect(date).toBeInstanceOf(Date)
    expect(dateToYyyymmdd(date!)).toBe('20260415')
  })

  it('returns null for empty/undefined YYYYMMDD input', () => {
    expect(yyyymmddToDate('')).toBeNull()
    expect(yyyymmddToDate(null)).toBeNull()
    expect(yyyymmddToDate(undefined)).toBeNull()
  })

  it('round-trips YYYYMM through Date', () => {
    expect(dateToYyyymm(yyyymmToDate('202612'))).toBe('202612')
    expect(dateToYyyymm(yyyymmToDate('202601'))).toBe('202601')
  })

  it('formats YYYYMMDD for display', () => {
    expect(formatYyyymmddDisplay('20260405')).toBe('2026-04-05')
  })

  it('todayYyyymmdd returns an 8-digit string', () => {
    expect(todayYyyymmdd()).toMatch(/^\d{8}$/)
  })
})
