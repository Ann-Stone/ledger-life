import { http } from 'msw'
import { ok, fail } from '../util'
import { _alarmsSnapshot, _budgetsForYear } from './settings'
import type {
  DashboardAlarm,
  DashboardBudget,
  DashboardBudgetLine,
  DashboardGift,
  DashboardSummary,
  RetirementReadiness,
  RetirementSetting,
  TargetSetting,
  TargetSettingCreate,
  TargetSettingUpdate,
} from '@/types/models'

// ─── Targets — in-memory CRUD ────────────────────────────────────────────────

let targets: TargetSetting[] = [
  { distinct_number: 'T1', target_year: '2026', setting_value: '年度淨值目標 18,000,000', is_done: 'N' },
  { distinct_number: 'T2', target_year: '2026', setting_value: '股票股利收入 1,200,000', is_done: 'N' },
  { distinct_number: 'T3', target_year: '2025', setting_value: '購入第二間房', is_done: 'Y' },
]

// ─── Summary points ──────────────────────────────────────────────────────────

function eachPeriod(period: string): string[] {
  const [start, end] = period.split('-')
  const startYM = start || '202505'
  const endYM = end || '202604'
  let y = Number(startYM.slice(0, 4))
  let m = Number(startYM.slice(4, 6))
  const endY = Number(endYM.slice(0, 4))
  const endM = Number(endYM.slice(4, 6))
  const out: string[] = []
  while (y < endY || (y === endY && m <= endM)) {
    out.push(`${y}${String(m).padStart(2, '0')}`)
    m += 1
    if (m === 13) { m = 1; y += 1 }
  }
  return out
}

function assetDebtPoints(period: string): DashboardSummary {
  // Hand-tuned monthly slopes for a readable stacked-area + net-worth demo.
  const points = eachPeriod(period).map((p, i) => {
    const accounts = 3_800_000 + i * 35_000
    const stocks = 5_200_000 + i * 60_000 + Math.round(Math.sin(i) * 80_000)
    const estates = 6_000_000
    const insurances = 1_400_000 + i * 12_000
    const loans = -2_500_000 + i * 18_000 // amortizing toward 0
    const cards = -680_000 + Math.round(Math.cos(i) * 40_000)
    const breakdown = { accounts, stocks, estates, insurances, loans, cards }
    const value = accounts + stocks + estates + insurances + loans + cards
    return { period: p, value, breakdown }
  })
  return { type: 'asset_debt_trend', points }
}

function freedomRatioPoints(period: string): DashboardSummary {
  // Income vs fixed_expenses so MoM/YoY on the rolling card carries signal.
  const points = eachPeriod(period).map((p, i) => {
    const income = 95_000 + Math.round(Math.sin(i * 0.7) * 12_000) + i * 600
    const fixed_expenses = 60_000 + Math.round(Math.cos(i * 0.5) * 5_000)
    const value = income > 0 ? (income - fixed_expenses) / income : 0
    return { period: p, value, breakdown: { income, fixed_expenses } }
  })
  return { type: 'freedom_ratio', points }
}

function spendingPoints(period: string): DashboardSummary {
  // Retained for any consumer still hitting the spending summary type.
  const points = eachPeriod(period).map((p, i) => ({
    period: p,
    value: 38_000 + Math.round(Math.sin(i) * 6_000) + i * 200,
  }))
  return { type: 'spending', points }
}

function workFreedomRatioPoints(period: string): DashboardSummary {
  // Passive grows slowly relative to active income so the rolling card has signal.
  const points = eachPeriod(period).map((p, i) => {
    const active = 80_000 + Math.round(Math.cos(i * 0.4) * 10_000) + i * 400
    const passive = 6_000 + Math.round(Math.sin(i * 0.6) * 2_000) + i * 300
    const total = passive + active
    const value = total > 0 ? passive / total : 0
    return { period: p, value, breakdown: { passive, active } }
  })
  return { type: 'work_freedom_ratio', points }
}

function summaryPoints(type: string, period: string): DashboardSummary {
  if (type === 'asset_debt_trend') return assetDebtPoints(period)
  if (type === 'freedom_ratio') return freedomRatioPoints(period)
  if (type === 'work_freedom_ratio') return workFreedomRatioPoints(period)
  return spendingPoints(period)
}

// ─── Budget overview ─────────────────────────────────────────────────────────

function dashboardBudget(type: string, period: string): DashboardBudget {
  const year = period.slice(0, 4)
  const monthIdx = type === 'monthly' ? Number(period.slice(4, 6)) : 0
  const yearBudgets = _budgetsForYear(year)
  const ordinary: DashboardBudgetLine[] = []
  const events: DashboardBudgetLine[] = []
  for (const b of yearBudgets) {
    if (b.code_type === 'Income' || b.code_type === 'Transfer') continue
    const isEvent = (b.annual_amount ?? 0) > 0
    if (isEvent) {
      const planned = Number(b.annual_amount) || 0
      // Monthly view → YTD actual through `monthIdx`; yearly → whole-year actual.
      const fraction = type === 'monthly' ? Math.min(1, monthIdx / 12) : 1
      const actual = Math.round(planned * fraction * (0.4 + Math.random() * 0.4))
      events.push({
        category: b.category_name,
        planned,
        actual,
        usage_pct: planned ? actual / planned : 0,
      })
    } else {
      let planned: number
      if (type === 'monthly') {
        const key = `expected${String(monthIdx).padStart(2, '0')}` as keyof typeof b
        planned = Number(b[key]) || 0
      } else {
        planned = (b.expected01 + b.expected02 + b.expected03 + b.expected04 + b.expected05 + b.expected06 + b.expected07 + b.expected08 + b.expected09 + b.expected10 + b.expected11 + b.expected12)
      }
      const actual = Math.round(planned * (0.55 + Math.random() * 0.4))
      ordinary.push({
        category: b.category_name,
        planned,
        actual,
        usage_pct: planned ? actual / planned : 0,
      })
    }
  }
  return {
    type,
    period,
    lines: ordinary,
    total_planned: ordinary.reduce((s, l) => s + l.planned, 0),
    total_actual: ordinary.reduce((s, l) => s + l.actual, 0),
    event_lines: events,
    event_total_planned: events.reduce((s, l) => s + l.planned, 0),
    event_total_actual: events.reduce((s, l) => s + l.actual, 0),
  }
}

// ─── Gifts ───────────────────────────────────────────────────────────────────

function dashboardGifts(_year: string): DashboardGift[] {
  return [
    { owner: '父',     amount: 60000, rate: 0.5 },
    { owner: '母',     amount: 60000, rate: 0.5 },
    { owner: '配偶',   amount: 30000, rate: 0.25 },
  ]
}

// ─── Alarms ──────────────────────────────────────────────────────────────────

function dashboardAlarms(): DashboardAlarm[] {
  const alarms = _alarmsSnapshot()
  const list: DashboardAlarm[] = []
  alarms.forEach((a) => {
    if (a.alarm_type === 'M') {
      // Monthly recurrence. alarm_date is DD (e.g. '10')
      // Let's generate for 20260510 and 20260610
      list.push({
        date: `202605${a.alarm_date.padStart(2, '0')}`,
        content: a.content,
        alarm_type: 'M',
      })
      list.push({
        date: `202606${a.alarm_date.padStart(2, '0')}`,
        content: a.content,
        alarm_type: 'M',
      })
    } else {
      // Yearly recurrence. alarm_date is MMDD (e.g. '0512')
      list.push({
        date: `2026${a.alarm_date}`,
        content: a.content,
        alarm_type: 'Y',
      })
    }
  })
  list.sort((x, y) => x.date.localeCompare(y.date))
  return list
}

// ─── Handlers ────────────────────────────────────────────────────────────────

// ─── Retirement readiness — in-memory state + derived snapshot ───────────────

const retirementSetting: RetirementSetting = {
  withdrawal_rate: 0.04,
  annual_expense_override: null,
  exclude_self_occupied_estate: true,
}

function retirementReadiness(): RetirementReadiness {
  const fullNetWorth = 8_000_000
  const selfOccupied = 3_000_000  // a self-occupied (live) home in the mock balance sheet
  const excluded = retirementSetting.exclude_self_occupied_estate ? selfOccupied : 0
  const netWorth = fullNetWorth - excluded
  const annualExpenseBase = retirementSetting.annual_expense_override ?? 600_000
  const rate = retirementSetting.withdrawal_rate || 0.04
  const target = Math.round(annualExpenseBase / rate)
  const monthlyIncome = 90_000
  const monthlyLoan = 28_000
  return {
    net_worth: netWorth,
    exclude_self_occupied_estate: retirementSetting.exclude_self_occupied_estate,
    self_occupied_estate_value: excluded,
    annual_expense_base: annualExpenseBase,
    expense_base_source: retirementSetting.annual_expense_override ? 'override' : 'computed',
    withdrawal_rate: rate,
    target_portfolio: target,
    readiness_pct: Math.round((netWorth / target) * 10000) / 10000,
    gap: target - netWorth,
    monthly_income: monthlyIncome,
    monthly_loan_payment: monthlyLoan,
    debt_service_ratio: Math.round((monthlyLoan / monthlyIncome) * 10000) / 10000,
    loans: [
      {
        loan_id: 'LN-001',
        loan_name: '房貸',
        remaining_balance: 3_200_000,
        monthly_payment: 28_000,
        payoff_month: '203406',
        years_left: 8.5,
      },
    ],
  }
}

export const dashboardHandlers = [
  http.get('*/dashboard/summary', ({ request }) => {
    const url = new URL(request.url)
    const type = url.searchParams.get('type') ?? 'monthly'
    const period = url.searchParams.get('period') ?? '202505-202604'
    return ok(summaryPoints(type, period))
  }),
  http.get('*/dashboard/alarms', () => ok(dashboardAlarms())),
  http.get('*/dashboard/targets', () => ok(targets)),
  http.post('*/dashboard/targets', async ({ request }) => {
    const body = (await request.json()) as TargetSettingCreate
    const maxSeen = targets.reduce((max, t) => {
      const num = parseInt(t.distinct_number.replace(/\D/g, ''), 10)
      return isNaN(num) ? max : Math.max(max, num)
    }, 0)
    const nextNum = `T${maxSeen + 1}`
    const created: TargetSetting = {
      distinct_number: nextNum,
      target_year: body.target_year ?? String(new Date().getFullYear()),
      setting_value: body.setting_value,
      is_done: body.is_done ?? 'N',
    }
    targets.push(created)
    return ok(created)
  }),
  http.put('*/dashboard/targets/:id', async ({ params, request }) => {
    const body = (await request.json()) as TargetSettingUpdate
    const idx = targets.findIndex((t) => t.distinct_number === String(params.id))
    const cur = targets[idx]
    if (!cur) return fail('target not found', 404)
    const next: TargetSetting = { ...cur, ...body }
    targets[idx] = next
    return ok(next)
  }),
  http.delete('*/dashboard/targets/:id', ({ params }) => {
    const before = targets.length
    targets = targets.filter((t) => t.distinct_number !== String(params.id))
    if (targets.length === before) return fail('target not found', 404)
    return ok(null)
  }),
  http.get('*/dashboard/budget', ({ request }) => {
    const url = new URL(request.url)
    const type = url.searchParams.get('type') ?? 'monthly'
    const period = url.searchParams.get('period') ?? '202604'
    return ok(dashboardBudget(type, period))
  }),
  http.get('*/dashboard/gifts/:year', ({ params }) => ok(dashboardGifts(String(params.year)))),
  http.get('*/dashboard/retirement-settings', () => ok(retirementSetting)),
  http.put('*/dashboard/retirement-settings', async ({ request }) => {
    const body = (await request.json()) as Partial<RetirementSetting>
    if (body.withdrawal_rate != null) retirementSetting.withdrawal_rate = body.withdrawal_rate
    retirementSetting.annual_expense_override =
      body.annual_expense_override && body.annual_expense_override > 0
        ? body.annual_expense_override
        : null
    if (body.exclude_self_occupied_estate != null)
      retirementSetting.exclude_self_occupied_estate = body.exclude_self_occupied_estate
    return ok(retirementSetting)
  }),
  http.get('*/dashboard/retirement', () => ok(retirementReadiness())),
]
