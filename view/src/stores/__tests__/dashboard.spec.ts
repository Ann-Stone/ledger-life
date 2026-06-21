import { describe, it, expect, beforeEach } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { nextTick } from 'vue'
import {
  useDashboardStore,
  summaryPeriodFor,
} from '@/stores/dashboard'
import type { DashboardSummary } from '@/types/models'

function makeFreedomSummary(
  points: Array<{ period: string; value: number; income?: number; fixed?: number }>,
): DashboardSummary {
  return {
    type: 'freedom_ratio',
    points: points.map((p) => ({
      period: p.period,
      value: p.value,
      breakdown:
        p.income === undefined && p.fixed === undefined
          ? undefined
          : { income: p.income ?? 0, fixed_expenses: p.fixed ?? 0 },
    })),
  }
}

describe('summaryPeriodFor', () => {
  it('month view: anchor extended back 13 months', () => {
    expect(summaryPeriodFor('month', '202605')).toBe('202505-202605')
  })

  it('month view: handles year wrap', () => {
    expect(summaryPeriodFor('month', '202601')).toBe('202501-202601')
  })

  it('year view: anchor year extended back 11 years (132 months)', () => {
    expect(summaryPeriodFor('year', '2026')).toBe('201601-202612')
  })
})

describe('useDashboardStore — freedomRatioCurrent (month view)', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('sums trailing 12 of the 13 fetched points', () => {
    const store = useDashboardStore()
    // 13 months: income=100 each, fixed=75 each → last 12 → (1200-900)/1200 = 0.25
    const points = Array.from({ length: 13 }, (_, i) => ({
      period: `2025${String((i % 12) + 1).padStart(2, '0')}`,
      value: 0.25,
      income: 100,
      fixed: 75,
    }))
    store.summaries.freedom_ratio = makeFreedomSummary(points)
    expect(store.freedomRatioCurrent).toBeCloseTo(0.25, 10)
  })

  it('returns 0 when total income is 0', () => {
    const store = useDashboardStore()
    store.summaries.freedom_ratio = makeFreedomSummary([
      { period: '202504', value: 0, income: 0, fixed: 0 },
      { period: '202505', value: 0, income: 0, fixed: 50 },
    ])
    expect(store.freedomRatioCurrent).toBe(0)
  })

  it('returns 0 when no freedom_ratio summary loaded', () => {
    const store = useDashboardStore()
    expect(store.freedomRatioCurrent).toBe(0)
  })
})

describe('useDashboardStore — freedomRatioCurrent (year view) + prev year delta', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('filters to anchor year only and computes prev-year value', () => {
    const store = useDashboardStore()
    store.setView('year', '2025')
    const points = [
      // 2024: income 100/mo, fixed 75/mo → ratio 0.25
      ...Array.from({ length: 12 }, (_, i) => ({
        period: `2024${String(i + 1).padStart(2, '0')}`,
        value: 0.25,
        income: 100,
        fixed: 75,
      })),
      // 2025: income 100/mo, fixed 50/mo → ratio 0.50
      ...Array.from({ length: 12 }, (_, i) => ({
        period: `2025${String(i + 1).padStart(2, '0')}`,
        value: 0.5,
        income: 100,
        fixed: 50,
      })),
    ]
    store.summaries.freedom_ratio = makeFreedomSummary(points)
    expect(store.freedomRatioCurrent).toBeCloseTo(0.5, 10)
    expect(store.freedomRatioPrevYear).toBeCloseTo(0.25, 10)
  })

  it('prev-year value is null in month view', () => {
    const store = useDashboardStore()
    // default view is month
    expect(store.freedomRatioPrevYear).toBeNull()
  })
})

function makeWorkFreedomSummary(
  points: Array<{ period: string; value: number; passive?: number; active?: number }>,
): DashboardSummary {
  return {
    type: 'work_freedom_ratio',
    points: points.map((p) => ({
      period: p.period,
      value: p.value,
      breakdown:
        p.passive === undefined && p.active === undefined
          ? undefined
          : { passive: p.passive ?? 0, active: p.active ?? 0 },
    })),
  }
}

describe('useDashboardStore — workFreedomRatioCurrent', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('month view: sums last 12 of 13 points → passive / (passive+active)', () => {
    const store = useDashboardStore()
    const points = Array.from({ length: 13 }, (_, i) => ({
      period: `2025${String((i % 12) + 1).padStart(2, '0')}`,
      value: 0.3,
      passive: 300,
      active: 700,
    }))
    store.summaries.work_freedom_ratio = makeWorkFreedomSummary(points)
    expect(store.workFreedomRatioCurrent).toBeCloseTo(0.3, 10)
  })

  it('returns 0 when total is 0', () => {
    const store = useDashboardStore()
    store.summaries.work_freedom_ratio = makeWorkFreedomSummary([
      { period: '202504', value: 0, passive: 0, active: 0 },
    ])
    expect(store.workFreedomRatioCurrent).toBe(0)
  })

  it('returns 0 when no summary loaded', () => {
    const store = useDashboardStore()
    expect(store.workFreedomRatioCurrent).toBe(0)
  })
})

describe('useDashboardStore — view state persistence', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
    localStorage.clear()
  })

  it('setView persists to localStorage', async () => {
    const store = useDashboardStore()
    store.setView('year', '2024')
    await nextTick()
    const raw = localStorage.getItem('dashboard.viewState')
    expect(raw).not.toBeNull()
    expect(JSON.parse(raw!)).toEqual({ viewMode: 'year', anchor: '2024' })
  })

  it('anchorYear derives from anchor (month vs year)', () => {
    const store = useDashboardStore()
    store.setView('month', '202403')
    expect(store.anchorYear).toBe('2024')
    store.setView('year', '2023')
    expect(store.anchorYear).toBe('2023')
  })
})
