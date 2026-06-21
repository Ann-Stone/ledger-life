import { http } from 'msw'
import { ok, fail } from '../util'
import type {
  Journal,
  JournalCreate,
  JournalUpdate,
  JournalListResponse,
  StockPriceEntry,
  StockPriceHistory,
  InsuranceValueMonth,
  InsuranceValueCreate,
  EstateValueMonth,
  EstateValueCreate,
  EstateValueSuggestion,
} from '@/types/models'

const CURRENT_MONTH = '202605'

let journals: Journal[] = [
  { distinct_number: 1, vesting_month: CURRENT_MONTH, spend_date: '20260503', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INC',  action_main_type: 'Income',   action_main_table: 'Code_Data', action_sub: 'INC_SAL',  action_sub_type: 'Income',   action_sub_table: 'Code_Data', spending: 80000, invoice_number: null, note: '5 月薪資' },
  { distinct_number: 2, vesting_month: CURRENT_MONTH, spend_date: '20260505', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'FIX',  action_main_type: 'Fixed',    action_main_table: 'Code_Data', action_sub: 'FIX_RNT',  action_sub_type: 'Fixed',    action_sub_table: 'Code_Data', spending: -18000, invoice_number: null, note: '5 月房租' },
  { distinct_number: 3, vesting_month: CURRENT_MONTH, spend_date: '20260508', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'FLT',  action_main_type: 'Floating', action_main_table: 'Code_Data', action_sub: 'FLT_FOOD', action_sub_type: 'Floating', action_sub_table: 'Code_Data', spending: -1280, invoice_number: 'AB-12345678', note: '聚餐' },
  { distinct_number: 4, vesting_month: CURRENT_MONTH, spend_date: '20260512', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'FLT',  action_main_type: 'Floating', action_main_table: 'Code_Data', action_sub: 'FLT_TRP',  action_sub_type: 'Floating', action_sub_table: 'Code_Data', spending: -540,  invoice_number: null, note: '高鐵' },
  { distinct_number: 5, vesting_month: CURRENT_MONTH, spend_date: '20260520', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INV',  action_main_type: 'Invest',   action_main_table: 'Code_Data', action_sub: 'INV_STK',  action_sub_type: 'Invest',   action_sub_table: 'Code_Data', spending: -15000, invoice_number: null, note: '台股定期定額' },
  { distinct_number: 6, vesting_month: CURRENT_MONTH, spend_date: '20260518', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'FIX',  action_main_type: 'Fixed',    action_main_table: 'Code_Data', action_sub: 'FIX_UTL',  action_sub_type: 'Fixed',    action_sub_table: 'Code_Data', spending: -2400, invoice_number: null, note: '電費' },
  { distinct_number: 7, vesting_month: '202604',     spend_date: '20260418', spend_way: 'BANK_CTBC', spend_way_type: 'account',     spend_way_table: 'Account',     action_main: 'INC',  action_main_type: 'Income',   action_main_table: 'Code_Data', action_sub: 'INC_SAL',  action_sub_type: 'Income',   action_sub_table: 'Code_Data', spending: 80000, invoice_number: null, note: '4 月薪資' },
  // Legacy e-invoice import shape: never classified → uncategorized banner/tag demo.
  { distinct_number: 8, vesting_month: CURRENT_MONTH, spend_date: '20260515', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'undefined', action_main_type: 'undefined', action_main_table: 'Code_Data', action_sub: '', action_sub_type: '', action_sub_table: '', spending: -320, invoice_number: 'CD-87654321', note: '超商' },
  { distinct_number: 9, vesting_month: '202604',     spend_date: '20260422', spend_way: 'CC_VISA',   spend_way_type: 'credit_card', spend_way_table: 'Credit_Card', action_main: 'No',        action_main_type: 'No',        action_main_table: 'Code_Data', action_sub: '', action_sub_type: '', action_sub_table: '', spending: -150, invoice_number: 'CD-11223344', note: '飲料店' },
]
let journalSeq = journals.length

function listForMonth(month: string): JournalListResponse {
  const items = journals.filter((j) => j.vesting_month === month)
  const gain_loss = items.reduce((sum, j) => sum + j.spending, 0)
  return { items, gain_loss }
}

// Mirrors api journal_types.is_uncategorized — anything outside the report buckets.
const KNOWN_MAIN_TYPES = new Set(['fixed', 'floating', 'income', 'passive', 'invest', 'transfer'])

function uncategorizedSummary() {
  const perMonth = new Map<string, number>()
  for (const j of journals) {
    if (KNOWN_MAIN_TYPES.has((j.action_main_type ?? '').trim().toLowerCase())) continue
    perMonth.set(j.vesting_month, (perMonth.get(j.vesting_month) ?? 0) + 1)
  }
  const months = [...perMonth.entries()]
    .sort((a, b) => (a[0] < b[0] ? 1 : -1))
    .map(([vesting_month, count]) => ({ vesting_month, count }))
  return { total: months.reduce((sum, m) => sum + m.count, 0), months }
}

// ─── Analytics fixtures ──────────────────────────────────────────────────────

function expenditureBudget() {
  return {
    rows: [
      { action_main_type: 'Fixed',    actual: 20400, expected: 21000, diff: 600,   usage_rate: 0.97 },
      { action_main_type: 'Floating', actual: 1820,  expected: 15000, diff: 13180, usage_rate: 0.12 },
      { action_main_type: 'Invest',   actual: 15000, expected: 15000, diff: 0,     usage_rate: 1.0  },
      { action_main_type: 'Income',   actual: 80000, expected: 90000, diff: 10000, usage_rate: 0.89 },
    ],
  }
}

function expenditureRatio() {
  return {
    outer: [
      { name: '固定支出', value: 20400 },
      { name: '浮動支出', value: 1820 },
      { name: '投資',   value: 15000 },
    ],
    inner: [
      { name: '房租', value: 18000 },
      { name: '水電', value: 2400 },
      { name: '伙食', value: 1280 },
      { name: '交通', value: 540 },
      { name: '股票', value: 15000 },
    ],
  }
}

function investRatio() {
  return {
    items: [
      { name: '台股 ETF', value: 9000 },
      { name: '美股',   value: 4500 },
      { name: '債券',   value: 1500 },
    ],
  }
}

function liability() {
  return {
    items: [
      { credit_card_id: 'CC_VISA', credit_card_name: 'Visa 御璽',   amount: 1820 },
      { credit_card_id: 'CC_MC',   credit_card_name: 'MasterCard 鈦金', amount: 0 },
      { credit_card_id: 'CC_AMEX', credit_card_name: 'Amex Gold',    amount: 0 },
    ],
  }
}

// ─── Stock prices ────────────────────────────────────────────────────────────

let stockPriceHistory: StockPriceHistory[] = [
  { stock_code: '0050', fetch_date: '20260530', open_price: 168.5, highest_price: 170.2, lowest_price: 167.0, close_price: 169.8 },
  { stock_code: '2330', fetch_date: '20260530', open_price: 920,   highest_price: 935,   lowest_price: 918,   close_price: 932   },
  // VOO only has an April row → no May data, surfaces as a "待補" row.
  { stock_code: 'VOO',  fetch_date: '20260430', open_price: 510,   highest_price: 514,   lowest_price: 508,   close_price: 512.5 },
]

const stockHoldings = [
  { stock_code: '0050', stock_name: '元大台灣 50' },
  { stock_code: '2330', stock_name: '台積電' },
  { stock_code: 'VOO',  stock_name: 'Vanguard S&P500' },
]

const insurancePolicies = [
  { insurance_id: 'INS-001', insurance_name: '富邦人壽終身壽險' },
  { insurance_id: 'INS-002', insurance_name: '南山儲蓄險' },
]

// Recorded surrender values; INS-002 has an entry, INS-001 surfaces as "待補".
let insuranceValueHistory: InsuranceValueCreate[] = [
  { insurance_id: 'INS-002', vesting_month: '202604', surrender_value: 312000 },
]

// Mirror the backend: latest recorded value on or before the month (carried
// forward); recorded is true only when entered in this exact month.
function currentSurrenderValues(month: string): InsuranceValueMonth[] {
  return insurancePolicies.map(({ insurance_id, insurance_name }) => {
    const latest = insuranceValueHistory
      .filter((v) => v.insurance_id === insurance_id && v.vesting_month <= month)
      .sort((a, b) => b.vesting_month.localeCompare(a.vesting_month))[0]
    return {
      insurance_id,
      insurance_name,
      surrender_value: latest ? latest.surrender_value : null,
      vesting_month: latest ? latest.vesting_month : null,
      recorded: !!latest && latest.vesting_month === month,
    }
  })
}

const estateHoldings = [
  { estate_id: 'EST-001', estate_name: '主要住所' },
  { estate_id: 'EST-002', estate_name: '投資宅 A' },
]

// EST-001 has a recorded appraisal; EST-002 surfaces as "待補".
let estateValueHistory: EstateValueCreate[] = [
  { estate_id: 'EST-001', vesting_month: '202604', market_value: 13800000 },
]

function currentMarketValues(month: string): EstateValueMonth[] {
  return estateHoldings.map(({ estate_id, estate_name }) => {
    const latest = estateValueHistory
      .filter((v) => v.estate_id === estate_id && v.vesting_month <= month)
      .sort((a, b) => b.vesting_month.localeCompare(a.vesting_month))[0]
    return {
      estate_id,
      estate_name,
      market_value: latest ? latest.market_value : null,
      vesting_month: latest ? latest.vesting_month : null,
      recorded: !!latest && latest.vesting_month === month,
    }
  })
}

// Mirror the backend: pick the most recent history row strictly within the
// requested month; emit null close_price / fetch_date when the month has none.
function currentPrices(month: string): StockPriceEntry[] {
  return stockHoldings.map(({ stock_code, stock_name }) => {
    const inMonth = stockPriceHistory
      .filter((h) => h.stock_code === stock_code && h.fetch_date.slice(0, 6) === month)
      .sort((a, b) => b.fetch_date.localeCompare(a.fetch_date))[0]
    return {
      stock_code,
      stock_name,
      close_price: inMonth ? inMonth.close_price : null,
      fetch_date: inMonth ? inMonth.fetch_date : null,
    }
  })
}

// ─── Handlers ────────────────────────────────────────────────────────────────

export const monthlyReportHandlers = [
  // Journal CRUD — specific paths first
  http.get('*/monthly-report/journals/:month/expenditure-budget', () => ok(expenditureBudget())),
  http.get('*/monthly-report/journals/:month/expenditure-ratio',  () => ok(expenditureRatio())),
  http.get('*/monthly-report/journals/:month/invest-ratio',       () => ok(investRatio())),
  http.get('*/monthly-report/journals/:month/liability',          () => ok(liability())),
  // Static path must precede the ':month' catch-all (same rule as the FastAPI router).
  http.get('*/monthly-report/journals/uncategorized-summary', () => ok(uncategorizedSummary())),
  http.get('*/monthly-report/journals/:month', ({ params }) => ok(listForMonth(String(params.month)))),
  http.post('*/monthly-report/journals', async ({ request }) => {
    const body = (await request.json()) as JournalCreate
    journalSeq += 1
    const created: Journal = {
      distinct_number: journalSeq,
      vesting_month: body.vesting_month,
      spend_date: body.spend_date,
      spend_way: body.spend_way,
      spend_way_type: body.spend_way_type,
      spend_way_table: body.spend_way_table,
      action_main: body.action_main,
      action_main_type: body.action_main_type,
      action_main_table: body.action_main_table,
      action_sub: body.action_sub ?? null,
      action_sub_type: body.action_sub_type ?? null,
      action_sub_table: body.action_sub_table ?? null,
      spending: body.spending,
      invoice_number: body.invoice_number ?? null,
      note: body.note ?? null,
    }
    journals.push(created)
    return ok(created)
  }),
  // Composite endpoint: Journal + Stock_Detail in one atomic write.
  // The mock mirrors backend behaviour: excute_price = journal.spending
  // (signed pass-through), account is resolved from journal.spend_way.
  http.post('*/monthly-report/journals/stock-transaction', async ({ request }) => {
    const body = (await request.json()) as {
      journal: JournalCreate
      stock_detail: {
        stock_id: string
        excute_type: 'buy' | 'sell' | 'stock' | 'cash'
        excute_amount?: number
        excute_date?: string | null
        memo?: string | null
      }
    }
    journalSeq += 1
    const j: Journal = {
      distinct_number: journalSeq,
      vesting_month: body.journal.vesting_month,
      spend_date: body.journal.spend_date,
      spend_way: body.journal.spend_way,
      spend_way_type: body.journal.spend_way_type,
      spend_way_table: body.journal.spend_way_table,
      action_main: body.journal.action_main,
      action_main_type: body.journal.action_main_type,
      action_main_table: body.journal.action_main_table,
      action_sub: body.journal.action_sub ?? null,
      action_sub_type: body.journal.action_sub_type ?? null,
      action_sub_table: body.journal.action_sub_table ?? null,
      spending: body.journal.spending,
      invoice_number: body.journal.invoice_number ?? null,
      note: body.journal.note ?? null,
    }
    journals.push(j)
    const stock_detail = {
      distinct_number: journalSeq + 1000,
      stock_id: body.stock_detail.stock_id,
      excute_type: body.stock_detail.excute_type,
      excute_amount: body.stock_detail.excute_amount ?? 0,
      excute_price: j.spending,
      excute_date: body.stock_detail.excute_date || j.spend_date,
      account_id: j.spend_way,
      account_name: j.spend_way,
      memo: body.stock_detail.memo ?? j.note,
    }
    return ok({ journal: j, stock_detail })
  }),
  // Composite update: PUT /journals/:id/stock-transaction — mirrors the
  // backend's atomic-update semantics for re-classifying a previously-untagged
  // journal as a stock transaction (excute_price = signed journal.spending).
  http.put('*/monthly-report/journals/:id/stock-transaction', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as {
      journal: JournalUpdate
      stock_detail: {
        stock_id: string
        excute_type: 'buy' | 'sell' | 'stock' | 'cash'
        excute_amount?: number
        excute_date?: string | null
        memo?: string | null
      }
    }
    const idx = journals.findIndex((j) => j.distinct_number === id)
    const cur = journals[idx]
    if (!cur) return fail('journal not found', 404)
    const next: Journal = { ...cur, ...body.journal }
    journals[idx] = next
    const stock_detail = {
      distinct_number: id + 2000,
      stock_id: body.stock_detail.stock_id,
      excute_type: body.stock_detail.excute_type,
      excute_amount: body.stock_detail.excute_amount ?? 0,
      excute_price: next.spending,
      excute_date: body.stock_detail.excute_date || next.spend_date,
      account_id: next.spend_way,
      account_name: next.spend_way,
      memo: body.stock_detail.memo ?? next.note,
    }
    return ok({ journal: next, stock_detail })
  }),
  // Composite endpoint: Journal + Insurance_Journal in one atomic write.
  // Mirrors backend: excute_price = journal.spending (signed pass-through);
  // Insurance_Journal carries no settling source.
  http.post('*/monthly-report/journals/insurance-transaction', async ({ request }) => {
    const body = (await request.json()) as {
      journal: JournalCreate
      insurance_detail: {
        insurance_id: string
        insurance_excute_type: 'pay' | 'cash' | 'return' | 'expect'
        excute_date?: string | null
        memo?: string | null
      }
    }
    journalSeq += 1
    const j: Journal = {
      distinct_number: journalSeq,
      vesting_month: body.journal.vesting_month,
      spend_date: body.journal.spend_date,
      spend_way: body.journal.spend_way,
      spend_way_type: body.journal.spend_way_type,
      spend_way_table: body.journal.spend_way_table,
      action_main: body.journal.action_main,
      action_main_type: body.journal.action_main_type,
      action_main_table: body.journal.action_main_table,
      action_sub: body.journal.action_sub ?? null,
      action_sub_type: body.journal.action_sub_type ?? null,
      action_sub_table: body.journal.action_sub_table ?? null,
      spending: body.journal.spending,
      invoice_number: body.journal.invoice_number ?? null,
      note: body.journal.note ?? null,
    }
    journals.push(j)
    const insurance_detail = {
      distinct_number: journalSeq + 1000,
      insurance_id: body.insurance_detail.insurance_id,
      insurance_excute_type: body.insurance_detail.insurance_excute_type,
      excute_price: j.spending,
      excute_date: body.insurance_detail.excute_date || j.spend_date,
      memo: body.insurance_detail.memo ?? j.note,
    }
    return ok({ journal: j, insurance_detail })
  }),
  http.put('*/monthly-report/journals/:id/insurance-transaction', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as {
      journal: JournalUpdate
      insurance_detail: {
        insurance_id: string
        insurance_excute_type: 'pay' | 'cash' | 'return' | 'expect'
        excute_date?: string | null
        memo?: string | null
      }
    }
    const idx = journals.findIndex((j) => j.distinct_number === id)
    const cur = journals[idx]
    if (!cur) return fail('journal not found', 404)
    const next: Journal = { ...cur, ...body.journal }
    journals[idx] = next
    const insurance_detail = {
      distinct_number: id + 2000,
      insurance_id: body.insurance_detail.insurance_id,
      insurance_excute_type: body.insurance_detail.insurance_excute_type,
      excute_price: next.spending,
      excute_date: body.insurance_detail.excute_date || next.spend_date,
      memo: body.insurance_detail.memo ?? next.note,
    }
    return ok({ journal: next, insurance_detail })
  }),
  // Composite endpoint: Journal + Estate_Journal in one atomic write.
  http.post('*/monthly-report/journals/estate-transaction', async ({ request }) => {
    const body = (await request.json()) as {
      journal: JournalCreate
      estate_detail: {
        estate_id: string
        estate_excute_type: 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit'
        excute_date?: string | null
        memo?: string | null
      }
    }
    journalSeq += 1
    const j: Journal = {
      distinct_number: journalSeq,
      vesting_month: body.journal.vesting_month,
      spend_date: body.journal.spend_date,
      spend_way: body.journal.spend_way,
      spend_way_type: body.journal.spend_way_type,
      spend_way_table: body.journal.spend_way_table,
      action_main: body.journal.action_main,
      action_main_type: body.journal.action_main_type,
      action_main_table: body.journal.action_main_table,
      action_sub: body.journal.action_sub ?? null,
      action_sub_type: body.journal.action_sub_type ?? null,
      action_sub_table: body.journal.action_sub_table ?? null,
      spending: body.journal.spending,
      invoice_number: body.journal.invoice_number ?? null,
      note: body.journal.note ?? null,
    }
    journals.push(j)
    const estate_detail = {
      distinct_number: journalSeq + 1000,
      estate_id: body.estate_detail.estate_id,
      estate_excute_type: body.estate_detail.estate_excute_type,
      excute_price: j.spending,
      excute_date: body.estate_detail.excute_date || j.spend_date,
      memo: body.estate_detail.memo ?? j.note,
    }
    return ok({ journal: j, estate_detail })
  }),
  http.put('*/monthly-report/journals/:id/estate-transaction', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as {
      journal: JournalUpdate
      estate_detail: {
        estate_id: string
        estate_excute_type: 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit'
        excute_date?: string | null
        memo?: string | null
      }
    }
    const idx = journals.findIndex((j) => j.distinct_number === id)
    const cur = journals[idx]
    if (!cur) return fail('journal not found', 404)
    const next: Journal = { ...cur, ...body.journal }
    journals[idx] = next
    const estate_detail = {
      distinct_number: id + 2000,
      estate_id: body.estate_detail.estate_id,
      estate_excute_type: body.estate_detail.estate_excute_type,
      excute_price: next.spending,
      excute_date: body.estate_detail.excute_date || next.spend_date,
      memo: body.estate_detail.memo ?? next.note,
    }
    return ok({ journal: next, estate_detail })
  }),
  http.put('*/monthly-report/journals/:id', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as JournalUpdate
    const idx = journals.findIndex((j) => j.distinct_number === id)
    const cur = journals[idx]
    if (!cur) return fail('journal not found', 404)
    const next: Journal = { ...cur, ...body }
    journals[idx] = next
    return ok(next)
  }),
  http.delete('*/monthly-report/journals/:id', ({ params }) => {
    const id = Number(params.id)
    const before = journals.length
    journals = journals.filter((j) => j.distinct_number !== id)
    if (journals.length === before) return fail('journal not found', 404)
    return ok(null)
  }),

  // Settle
  http.put('*/monthly-report/balance/:month/settle', ({ params }) =>
    ok({
      vesting_month: String(params.month),
      estate_rows: 2,
      insurance_rows: 3,
      loan_rows: 2,
      stock_rows: 4,
      account_rows: 3,
      credit_card_rows: 3,
    }),
  ),

  // Stock prices
  http.get('*/monthly-report/stock-prices/:month', ({ params }) =>
    ok(currentPrices(String(params.month))),
  ),
  http.post('*/monthly-report/stock-prices', async ({ request }) => {
    const body = (await request.json()) as StockPriceHistory
    stockPriceHistory = stockPriceHistory.filter(
      (h) => !(h.stock_code === body.stock_code && h.fetch_date === body.fetch_date),
    )
    stockPriceHistory.push(body)
    return ok(body)
  }),

  // Insurance surrender values (解約金)
  http.get('*/monthly-report/insurance-values/:month', ({ params }) =>
    ok(currentSurrenderValues(String(params.month))),
  ),
  http.post('*/monthly-report/insurance-values', async ({ request }) => {
    const body = (await request.json()) as InsuranceValueCreate
    insuranceValueHistory = insuranceValueHistory.filter(
      (v) => !(v.insurance_id === body.insurance_id && v.vesting_month === body.vesting_month),
    )
    insuranceValueHistory.push(body)
    return ok(body)
  }),

  // Estate market values (估值)
  http.get('*/monthly-report/estate-values/:month', ({ params }) =>
    ok(currentMarketValues(String(params.month))),
  ),
  http.post('*/monthly-report/estate-values', async ({ request }) => {
    const body = (await request.json()) as EstateValueCreate
    estateValueHistory = estateValueHistory.filter(
      (v) => !(v.estate_id === body.estate_id && v.vesting_month === body.vesting_month),
    )
    estateValueHistory.push(body)
    return ok(body)
  }),
  http.get('*/monthly-report/estate-values/:month/suggestions', () => {
    const suggestions: EstateValueSuggestion[] = [
      { estate_id: 'EST-001', estate_name: '主要住所', cost: 10000000, suggested_market_value: 13800000, region: '臺北市全市', obtain_quarter: '2020Q1', current_quarter: '2024Q1' },
      { estate_id: 'EST-002', estate_name: '投資宅 A',  cost: 8000000,  suggested_market_value: 9600000,  region: '臺北市全市', obtain_quarter: '2021Q2', current_quarter: '2024Q1' },
    ]
    return ok(suggestions)
  }),
  http.post('*/monthly-report/estate-values/refresh-index', () =>
    ok({ region: '臺北市全市', upserted: 48, ok: true }),
  ),
]
