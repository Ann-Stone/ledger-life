import { defineStore } from 'pinia'
import { computed, ref, watch } from 'vue'
import dayjs from 'dayjs'
import { useFetchState } from '@/composables/useFetchState'
import {
  getDashboardBudget,
  getDashboardGifts,
  getDashboardSummary,
  getTargets,
} from '@/api/dashboard'
import { getUncategorizedSummary } from '@/api/cashFlow'
import type {
  DashboardGift,
  DashboardSummary,
  TargetSetting,
} from '@/types/models'

export type ViewMode = 'month' | 'year'

// MONTH view: trailing 13 months (12 + anchor) — 13 lets KPI cards compute YoY (last vs first).
// YEAR view: trailing 11 years (10 + anchor) of monthly data — frontend filters to year-end snapshots.
const MONTH_VIEW_WINDOW = 13
const YEAR_VIEW_WINDOW_YEARS = 11

const STORAGE_KEY = 'dashboard.viewState'

function loadPersisted(): { viewMode: ViewMode; anchor: string } {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (parsed.viewMode === 'month' && /^\d{6}$/.test(parsed.anchor)) return parsed
      if (parsed.viewMode === 'year' && /^\d{4}$/.test(parsed.anchor)) return parsed
    }
  } catch {
    // ignore — fall through to defaults
  }
  return { viewMode: 'month', anchor: dayjs().format('YYYYMM') }
}

export function summaryPeriodFor(
  viewMode: ViewMode,
  anchor: string,
): string {
  if (viewMode === 'month') {
    const end = dayjs(`${anchor}01`, 'YYYYMMDD')
    const start = end.subtract(MONTH_VIEW_WINDOW - 1, 'month')
    return `${start.format('YYYYMM')}-${end.format('YYYYMM')}`
  }
  const endYear = Number(anchor)
  const startYear = endYear - (YEAR_VIEW_WINDOW_YEARS - 1)
  return `${startYear}01-${endYear}12`
}

export type SummaryType =
  | 'spending'
  | 'freedom_ratio'
  | 'asset_debt_trend'
  | 'work_freedom_ratio'

export interface DashboardSummaryParams {
  type: SummaryType
  period: string
}

export interface DashboardBudgetParams {
  type: 'monthly' | 'yearly'
  period: string
}

const emptySummaryMap = (): Record<SummaryType, DashboardSummary | null> => ({
  spending: null,
  freedom_ratio: null,
  asset_debt_trend: null,
  work_freedom_ratio: null,
})

const emptyLoadingMap = (): Record<SummaryType, boolean> => ({
  spending: false,
  freedom_ratio: false,
  asset_debt_trend: false,
  work_freedom_ratio: false,
})

export const useDashboardStore = defineStore('dashboard', () => {
  // View state ----------------------------------------------------------------
  const persisted = loadPersisted()
  const viewMode = ref<ViewMode>(persisted.viewMode)
  const anchor = ref<string>(persisted.anchor)  // YYYYMM in month mode, YYYY in year mode

  watch([viewMode, anchor], ([m, a]) => {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify({ viewMode: m, anchor: a }))
    } catch {
      // ignore storage quota errors — view state is non-critical
    }
  })

  // anchorYear: which year the gifts/budget yearly call should target
  const anchorYear = computed(() =>
    viewMode.value === 'year' ? anchor.value : anchor.value.slice(0, 4),
  )

  // Summary -------------------------------------------------------------------
  const summaries = ref<Record<SummaryType, DashboardSummary | null>>(emptySummaryMap())
  const summariesLoading = ref<Record<SummaryType, boolean>>(emptyLoadingMap())
  async function fetchSummary(params: DashboardSummaryParams) {
    summariesLoading.value[params.type] = true
    try {
      summaries.value[params.type] = await getDashboardSummary(params)
    } finally {
      summariesLoading.value[params.type] = false
    }
  }

  async function fetchSummariesForDashboard() {
    const period = summaryPeriodFor(viewMode.value, anchor.value)
    await Promise.all([
      fetchSummary({ type: 'asset_debt_trend', period }),
      fetchSummary({ type: 'freedom_ratio', period }),
      fetchSummary({ type: 'work_freedom_ratio', period }),
    ])
  }

  // Freedom ratio aggregation -------------------------------------------------
  // Month view: rolling 12M ending at anchor month (use last 12 of the 13 fetched points).
  // Year view: anchor year only (12 months matching anchor year).
  function sliceFreedomPoints(year: string | null) {
    const points = summaries.value.freedom_ratio?.points ?? []
    if (year !== null) return points.filter((p) => p.period.startsWith(year))
    return points.slice(-12)
  }

  function sliceWorkFreedomPoints(year: string | null) {
    const points = summaries.value.work_freedom_ratio?.points ?? []
    if (year !== null) return points.filter((p) => p.period.startsWith(year))
    return points.slice(-12)
  }

  const freedomRatioCurrent = computed<number>(() => {
    const pts = sliceFreedomPoints(viewMode.value === 'year' ? anchor.value : null)
    let income = 0
    let fixed = 0
    for (const p of pts) {
      income += p.breakdown?.income ?? 0
      fixed += p.breakdown?.fixed_expenses ?? 0
    }
    return income > 0 ? (income - fixed) / income : 0
  })

  const workFreedomRatioCurrent = computed<number>(() => {
    const pts = sliceWorkFreedomPoints(viewMode.value === 'year' ? anchor.value : null)
    let passive = 0
    let active = 0
    for (const p of pts) {
      passive += p.breakdown?.passive ?? 0
      active += p.breakdown?.active ?? 0
    }
    const total = passive + active
    return total > 0 ? passive / total : 0
  })

  // Year-view delta: anchor year vs previous year ratios.
  const freedomRatioPrevYear = computed<number | null>(() => {
    if (viewMode.value !== 'year') return null
    const prev = String(Number(anchor.value) - 1)
    const pts = sliceFreedomPoints(prev)
    if (pts.length === 0) return null
    let income = 0
    let fixed = 0
    for (const p of pts) {
      income += p.breakdown?.income ?? 0
      fixed += p.breakdown?.fixed_expenses ?? 0
    }
    return income > 0 ? (income - fixed) / income : 0
  })

  const workFreedomRatioPrevYear = computed<number | null>(() => {
    if (viewMode.value !== 'year') return null
    const prev = String(Number(anchor.value) - 1)
    const pts = sliceWorkFreedomPoints(prev)
    if (pts.length === 0) return null
    let passive = 0
    let active = 0
    for (const p of pts) {
      passive += p.breakdown?.passive ?? 0
      active += p.breakdown?.active ?? 0
    }
    const total = passive + active
    return total > 0 ? passive / total : 0
  })

  // Targets -------------------------------------------------------------------
  const targetsState = useFetchState(() => getTargets(), [] as TargetSetting[])

  // Budget --------------------------------------------------------------------
  const budgetState = useFetchState((params: DashboardBudgetParams) =>
    getDashboardBudget(params),
  )

  async function fetchBudgetForView() {
    if (viewMode.value === 'month') {
      await budgetState.fetch({ type: 'monthly', period: anchor.value })
    } else {
      await budgetState.fetch({ type: 'yearly', period: anchor.value })
    }
  }

  // Gifts ---------------------------------------------------------------------
  const giftsState = useFetchState(
    (year: number | string) => getDashboardGifts(year),
    [] as DashboardGift[],
  )

  async function fetchGiftsForView() {
    await giftsState.fetch(anchorYear.value)
  }

  // Uncategorized journals ------------------------------------------------------
  // Legacy 'undefined'/'No'/'' rows the reports can't bucket — powers the
  // cleanup banner that deep-links into 月度帳務.
  const uncategorizedState = useFetchState(() => getUncategorizedSummary())

  // Combined refetch ----------------------------------------------------------
  async function refetchAllForView() {
    await Promise.all([
      fetchSummariesForDashboard(),
      fetchBudgetForView(),
      fetchGiftsForView(),
    ])
  }

  function setView(nextMode: ViewMode, nextAnchor: string) {
    viewMode.value = nextMode
    anchor.value = nextAnchor
  }

  return {
    // View state
    viewMode,
    anchor,
    anchorYear,
    setView,
    // Summary
    summaries,
    summariesLoading,
    fetchSummary,
    fetchSummariesForDashboard,
    freedomRatioCurrent,
    workFreedomRatioCurrent,
    freedomRatioPrevYear,
    workFreedomRatioPrevYear,
    // Targets
    targets: targetsState.data,
    targetsLoading: targetsState.loading,
    fetchTargets: targetsState.fetch,
    // Budget
    budget: budgetState.data,
    budgetLoading: budgetState.loading,
    fetchBudget: budgetState.fetch,
    fetchBudgetForView,
    // Gifts
    gifts: giftsState.data,
    giftsLoading: giftsState.loading,
    fetchGifts: giftsState.fetch,
    fetchGiftsForView,
    // Uncategorized journals
    uncategorized: uncategorizedState.data,
    fetchUncategorized: uncategorizedState.fetch,
    // Combined
    refetchAllForView,
  }
})
