import { http } from 'msw'
import { ok } from '../util'
import type {
  AssetReport,
  BalanceReport,
  BudgetVariance,
  BudgetVarianceRow,
  CashFlow,
  CashFlowPoint,
  ExpenditureCategoryNode,
  ExpenditureComposition,
  ExpenditureReport,
  ExpenseInsights,
  IncomeExpensePoint,
  IncomeExpenseReport,
  IncomeStatementPoint,
  IncomeStatementReport,
  LargeTxn,
  StockAllocationReport,
  YoYRow,
} from '@/types/models'

const balance: BalanceReport = {
  assets: {
    accounts: [
      { name: '現金 (TWD)', amount: 125000, original_amount: 125000, currency: 'TWD' },
      { name: '中信活存',   amount: 480000, original_amount: 480000, currency: 'TWD' },
      { name: 'Wise USD',  amount: 240000, original_amount: 7500,    currency: 'USD' },
      { name: '日本郵貯',   amount: 90000,  original_amount: 400000, currency: 'JPY' },
    ],
    estates: [
      { name: '主要住所', amount: 12500000, original_amount: 12500000, currency: 'TWD' },
      { name: '投資宅 A', amount: 8500000,  original_amount: 8500000,  currency: 'TWD' },
      { name: '美國公寓', amount: 4800000,  original_amount: 150000,    currency: 'USD' },
    ],
    insurances: [
      { name: '終身壽險',   amount: 320000, original_amount: 320000, currency: 'TWD' },
      { name: '醫療險',     amount: 80000,  original_amount: 80000,  currency: 'TWD' },
      { name: '美元儲蓄險', amount: 480000, original_amount: 15000,  currency: 'USD' },
    ],
    stocks: [
      { name: '元大台灣 50',     amount: 169800, original_amount: 169800,  currency: 'TWD' },
      { name: '台積電',         amount: 372800, original_amount: 372800,  currency: 'TWD' },
      { name: 'Vanguard S&P500', amount: 192500, original_amount: 6015.63, currency: 'USD' },
    ],
  },
  liabilities: {
    credit_cards: [
      { name: 'Visa 御璽', amount: 1820, original_amount: 1820, currency: 'TWD' },
    ],
    loans: [
      { name: '房貸主貸', amount: 6800000, original_amount: 6800000, currency: 'TWD' },
      { name: '車貸',     amount: 480000,  original_amount: 480000,  currency: 'TWD' },
      { name: '信貸',     amount: 400000,  original_amount: 400000,  currency: 'TWD' },
      { name: '美國房貸', amount: 2880000, original_amount: 90000,   currency: 'USD' },
    ],
  },
  net_worth: 17788280,
}

function expenditureSeries(type: string, vestingMonth: string): ExpenditureReport {
  const baseYear = Number(vestingMonth.slice(0, 4))
  if (type === 'yearly') {
    return {
      type,
      points: [
        { period: String(baseYear - 2), amount: 480000 },
        { period: String(baseYear - 1), amount: 520000 },
        { period: String(baseYear),     amount: 560000 },
      ],
    }
  }
  // monthly default — 12 points ending at vestingMonth
  const points: { period: string; amount: number }[] = []
  let y = baseYear
  let m = Number(vestingMonth.slice(4, 6))
  for (let i = 0; i < 12; i++) {
    points.unshift({ period: `${y}${String(m).padStart(2, '0')}`, amount: 32000 + Math.round(Math.sin(i) * 6000) })
    m -= 1
    if (m === 0) { m = 12; y -= 1 }
  }
  return { type, points }
}

function incomeExpenseSeries(type: string, vestingMonth: string): IncomeExpenseReport {
  const baseYear = Number(vestingMonth.slice(0, 4))
  const points: IncomeExpensePoint[] = []
  if (type === 'yearly') {
    for (let i = 2; i >= 0; i--) {
      const income = 880000 + (2 - i) * 60000
      const fixed = 300000 + (2 - i) * 8000
      const floating = 180000 + Math.round(Math.cos(i) * 20000)
      const expense = fixed + floating
      points.push({
        period: String(baseYear - i),
        income,
        fixed,
        floating,
        expense,
        net: income - expense,
      })
    }
  } else {
    let y = baseYear
    let m = Number(vestingMonth.slice(4, 6))
    for (let i = 0; i < 12; i++) {
      const income = 72000 + Math.round(Math.sin(i) * 8000)
      const fixed = 25000
      const floating = 15000 + Math.round(Math.abs(Math.sin(i * 1.3)) * 9000)
      const expense = fixed + floating
      points.unshift({
        period: `${y}${String(m).padStart(2, '0')}`,
        income,
        fixed,
        floating,
        expense,
        net: income - expense,
      })
      m -= 1
      if (m === 0) {
        m = 12
        y -= 1
      }
    }
  }
  const total_income = points.reduce((s, p) => s + p.income, 0)
  const total_expense = points.reduce((s, p) => s + p.expense, 0)
  const net = total_income - total_expense
  const savings_rate = total_income ? net / total_income : 0
  return { type, points, summary: { total_income, total_expense, net, savings_rate } }
}

function incomeStatementSeries(type: string, vestingMonth: string): IncomeStatementReport {
  const baseYear = Number(vestingMonth.slice(0, 4))
  const points: IncomeStatementPoint[] = []
  const make = (period: string, i: number, scale: number): IncomeStatementPoint => {
    const active = Math.round((72000 + Math.sin(i) * 8000) * scale)
    const fixed = Math.round(25000 * scale)
    const floating = Math.round((15000 + Math.abs(Math.sin(i * 1.3)) * 9000) * scale)
    const dividend = Math.round((1800 + Math.abs(Math.cos(i)) * 1500) * scale)
    const realized = Math.round(Math.sin(i * 0.7) * 6000 * scale)
    const unrealized = Math.round(Math.cos(i * 0.9) * 14000 * scale)
    const loan_interest = 0
    const operating_net = active - fixed - floating - loan_interest
    const investment_net = dividend + realized + unrealized
    return {
      period,
      active_income: active,
      fixed,
      floating,
      loan_interest,
      operating_net,
      dividend,
      realized,
      unrealized,
      investment_net,
      comprehensive_net: operating_net + investment_net,
    }
  }
  if (type === 'yearly') {
    for (let i = 2; i >= 0; i--) {
      points.push(make(String(baseYear - i), i, 12))
    }
  } else {
    let y = baseYear
    let m = Number(vestingMonth.slice(4, 6))
    for (let i = 0; i < 12; i++) {
      points.unshift(make(`${y}${String(m).padStart(2, '0')}`, i, 1))
      m -= 1
      if (m === 0) {
        m = 12
        y -= 1
      }
    }
  }
  const sum = (k: keyof IncomeStatementPoint) =>
    points.reduce((s, p) => s + (p[k] as number), 0)
  return {
    type,
    points,
    summary: {
      active_income: sum('active_income'),
      fixed: sum('fixed'),
      floating: sum('floating'),
      loan_interest: sum('loan_interest'),
      operating_net: sum('operating_net'),
      dividend: sum('dividend'),
      realized: sum('realized'),
      unrealized: sum('unrealized'),
      investment_net: sum('investment_net'),
      comprehensive_net: sum('comprehensive_net'),
    },
  }
}

function expenditureComposition(): ExpenditureComposition {
  const categories: ExpenditureCategoryNode[] = [
    {
      code: 'F01', name: '居住', type: 'Fixed', amount: 360000, share: 0,
      children: [
        { code: 'F0101', name: '房貸/房租', amount: 300000, share: 0 },
        { code: 'F0102', name: '管理費', amount: 60000, share: 0 },
      ],
    },
    {
      code: 'E01', name: '餐飲', type: 'Floating', amount: 192000, share: 0,
      children: [
        { code: 'E0101', name: '外食', amount: 120000, share: 0 },
        { code: 'E0102', name: '食材', amount: 48000, share: 0 },
        { code: '', name: '未細分', amount: 24000, share: 0 },
      ],
    },
    { code: 'F02', name: '保險', type: 'Fixed', amount: 96000, share: 0, children: [] },
    {
      code: 'E02', name: '交通', type: 'Floating', amount: 78000, share: 0,
      children: [
        { code: 'E0201', name: '油費', amount: 48000, share: 0 },
        { code: 'E0202', name: '停車', amount: 30000, share: 0 },
      ],
    },
    { code: 'E03', name: '娛樂', type: 'Floating', amount: 54000, share: 0, children: [] },
  ]
  const total = categories.reduce((s, c) => s + c.amount, 0)
  const fixedTotal = categories
    .filter((c) => c.type === 'Fixed')
    .reduce((s, c) => s + c.amount, 0)
  const pct = (n: number) => Math.round((n / total) * 1000) / 10
  for (const c of categories) {
    c.share = pct(c.amount)
    for (const ch of c.children) ch.share = pct(ch.amount)
  }
  return { total, fixed_total: fixedTotal, floating_total: total - fixedTotal, categories }
}

function budgetVariance(year: string): BudgetVariance {
  const rows: BudgetVarianceRow[] = [
    { code: 'F01', name: '居住', type: 'Fixed', expected: 360000, actual: 180000, diff: 0, usage_rate: 0 },
    { code: 'E01', name: '餐飲', type: 'Floating', expected: 180000, actual: 96000, diff: 0, usage_rate: 0 },
    { code: 'F02', name: '保險', type: 'Fixed', expected: 96000, actual: 96000, diff: 0, usage_rate: 0 },
    { code: 'E02', name: '交通', type: 'Floating', expected: 72000, actual: 39000, diff: 0, usage_rate: 0 },
    { code: 'E03', name: '娛樂', type: 'Floating', expected: 48000, actual: 60000, diff: 0, usage_rate: 0 },
  ]
  for (const r of rows) {
    r.diff = r.actual - r.expected
    r.usage_rate = r.expected ? Math.round((r.actual / r.expected) * 10000) / 10000 : 0
  }
  rows.sort((a, b) => b.actual - a.actual)
  const totalExpected = rows.reduce((s, r) => s + r.expected, 0)
  const totalActual = rows.reduce((s, r) => s + r.actual, 0)
  const elapsedMonths = 6
  return {
    year,
    rows,
    summary: {
      total_expected: totalExpected,
      total_actual: totalActual,
      total_diff: totalActual - totalExpected,
      usage_rate: totalExpected ? Math.round((totalActual / totalExpected) * 10000) / 10000 : 0,
      elapsed_months: elapsedMonths,
      projected_total: Math.round((totalActual / elapsedMonths) * 12 * 100) / 100,
    },
  }
}

function cashFlowSeries(type: string, vestingMonth: string): CashFlow {
  const baseYear = Number(vestingMonth.slice(0, 4))
  const points: CashFlowPoint[] = []
  let sIncome = 0
  let sLiving = 0
  let sInterest = 0
  let sInvesting = 0
  let sPrincipal = 0
  const make = (period: string, i: number, scale: number): CashFlowPoint => {
    const income = Math.round((72000 + Math.sin(i) * 8000) * scale)
    const living = -Math.round((40000 + Math.abs(Math.sin(i * 1.3)) * 9000) * scale)
    const interest = -Math.round(3000 * scale)
    const investing = Math.round(Math.sin(i * 0.7) * 15000 * scale)
    const principal = -Math.round(7000 * scale)
    sIncome += income
    sLiving += living
    sInterest += interest
    sInvesting += investing
    sPrincipal += principal
    const operating = income + living + interest
    return {
      period,
      operating,
      investing,
      financing: principal,
      net_change: operating + investing + principal,
    }
  }
  if (type === 'yearly') {
    for (let i = 2; i >= 0; i--) {
      points.push(make(String(baseYear - i), i, 12))
    }
  } else {
    let y = baseYear
    let m = Number(vestingMonth.slice(4, 6))
    for (let i = 0; i < 12; i++) {
      points.unshift(make(`${y}${String(m).padStart(2, '0')}`, i, 1))
      m -= 1
      if (m === 0) {
        m = 12
        y -= 1
      }
    }
  }
  const operatingNet = sIncome + sLiving + sInterest
  return {
    type,
    points,
    summary: {
      activities: [
        {
          key: 'operating',
          label: '生活',
          net: operatingNet,
          items: [
            { label: '收入', amount: sIncome },
            { label: '生活支出', amount: sLiving },
            { label: '貸款利息', amount: sInterest },
          ],
        },
        {
          key: 'investing',
          label: '投資',
          net: sInvesting,
          items: [{ label: '投資淨額', amount: sInvesting }],
        },
        {
          key: 'financing',
          label: '債務',
          net: sPrincipal,
          items: [{ label: '償還本金', amount: sPrincipal }],
        },
      ],
      net_change: operatingNet + sInvesting + sPrincipal,
    },
  }
}

function expenseInsights(year: string): ExpenseInsights {
  const yoy: YoYRow[] = [
    { code: 'F01', name: '居住', type: 'Fixed', current: 360000, previous: 312000, delta: 0, yoy_rate: 0 },
    { code: 'E01', name: '餐飲', type: 'Floating', current: 192000, previous: 168000, delta: 0, yoy_rate: 0 },
    { code: 'E02', name: '交通', type: 'Floating', current: 78000, previous: 96000, delta: 0, yoy_rate: 0 },
    { code: 'F02', name: '保險', type: 'Fixed', current: 96000, previous: 96000, delta: 0, yoy_rate: 0 },
    { code: 'E03', name: '娛樂', type: 'Floating', current: 60000, previous: 42000, delta: 0, yoy_rate: 0 },
  ]
  for (const r of yoy) {
    r.delta = r.current - r.previous
    r.yoy_rate = r.previous ? Math.round(((r.current - r.previous) / r.previous) * 10000) / 10000 : 0
  }
  yoy.sort((a, b) => Math.abs(b.delta) - Math.abs(a.delta))
  const largest: LargeTxn[] = [
    { date: `${year}0815`, category: '旅遊', amount: 85000, pay_way: 'Chase Sapphire', note: '日本機票' },
    { date: `${year}0203`, category: '居住', amount: 60000, pay_way: '中信房貸', note: '季度管理費' },
    { date: `${year}1124`, category: '娛樂', amount: 32000, pay_way: '玉山現金回饋', note: '演唱會' },
    { date: `${year}0530`, category: '餐飲', amount: 18000, pay_way: '現金', note: '家庭聚餐' },
    { date: `${year}0712`, category: '交通', amount: 15000, pay_way: '台新', note: '高鐵月票' },
  ]
  return { year, yoy, largest }
}

const assetReport: AssetReport = {
  total: 22810100,
  items: [
    { type: '存款',     amount: 845000,   share: 3.7 },
    { type: '不動產',   amount: 21000000, share: 92.0 },
    { type: '保單',     amount: 400000,   share: 1.8 },
    { type: '股票',     amount: 735100,   share: 3.2 },
    { type: '其他',     amount: -169000,  share: -0.7 },
  ],
}

const stockAllocation: StockAllocationReport = {
  total: 735100,
  items: [
    { category_id: 'SC-001', category_name: '成長型', amount: 542600, share: 73.8 },
    { category_id: 'SC-002', category_name: '債券',   amount: 110000, share: 15.0 },
    { category_id: null,     category_name: '未分類', amount: 82500,  share: 11.2 },
  ],
}

export const reportsHandlers = [
  http.get('*/reports/balance', () => ok(balance)),
  http.get('*/reports/expenditure/:type', ({ params, request }) => {
    const url = new URL(request.url)
    const month = url.searchParams.get('vesting_month') ?? '202604'
    return ok(expenditureSeries(String(params.type), month))
  }),
  http.get('*/reports/income-expense/:type', ({ params, request }) => {
    const url = new URL(request.url)
    const month = url.searchParams.get('vesting_month') ?? '202612'
    return ok(incomeExpenseSeries(String(params.type), month))
  }),
  http.get('*/reports/income-statement/:type', ({ params, request }) => {
    const url = new URL(request.url)
    const month = url.searchParams.get('vesting_month') ?? '202612'
    return ok(incomeStatementSeries(String(params.type), month))
  }),
  http.get('*/reports/expenditure-composition/:type', () => ok(expenditureComposition())),
  http.get('*/reports/budget-variance/:year', ({ params }) =>
    ok(budgetVariance(String(params.year))),
  ),
  http.get('*/reports/cash-flow/:type', ({ params, request }) => {
    const url = new URL(request.url)
    const month = url.searchParams.get('vesting_month') ?? '202612'
    return ok(cashFlowSeries(String(params.type), month))
  }),
  http.get('*/reports/expense-insights/:year', ({ params }) =>
    ok(expenseInsights(String(params.year))),
  ),
  http.get('*/reports/assets', () => ok(assetReport)),
  http.get('*/reports/stock-allocation', () => ok(stockAllocation)),
]
