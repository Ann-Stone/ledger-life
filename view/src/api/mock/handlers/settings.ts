import { http } from 'msw'
import { ok, fail } from '../util'
import type {
  Account,
  AccountCreate,
  AccountUpdate,
  Alarm,
  AlarmCreate,
  AlarmUpdate,
  Budget,
  CodeData,
  CodeDataCreate,
  CodeDataUpdate,
  CodeDataWithSub,
  CreditCard,
  CreditCardCreate,
  CreditCardUpdate,
  StockCategory,
  StockCategoryCreate,
  StockCategoryUpdate,
} from '@/types/models'

// ─── Accounts ────────────────────────────────────────────────────────────────

let accounts: Account[] = [
  { id: 1, account_id: 'CASH_TWD', name: '現金 (TWD)', account_type: 'cash', fx_code: 'TWD', is_calculate: 'Y', in_use: 'Y', discount: 1, memo: null, owner: 'self', account_index: 1 },
  { id: 2, account_id: 'BANK_CTBC', name: '中信活存', account_type: 'bank', fx_code: 'TWD', is_calculate: 'Y', in_use: 'Y', discount: 1, memo: '主薪轉帳戶', owner: 'self', account_index: 2 },
  { id: 3, account_id: 'BANK_USD', name: 'Wise USD', account_type: 'bank', fx_code: 'USD', is_calculate: 'Y', in_use: 'Y', discount: 1, memo: null, owner: 'self', account_index: 3 },
  { id: 4, account_id: 'BANK_OLD', name: '舊帳戶（停用）', account_type: 'bank', fx_code: 'TWD', is_calculate: 'N', in_use: 'N', discount: 1, memo: null, owner: 'self', account_index: 4 },
]
let accountSeq = accounts.length

// ─── Codes / Sub-codes ───────────────────────────────────────────────────────

let codes: CodeData[] = [
  { code_id: 'INC',  code_type: 'Income',   name: '收入',   parent_id: null, in_use: 'Y', code_index: 1, is_annual_event: false },
  { code_id: 'FIX',  code_type: 'Fixed',    name: '固定支出', parent_id: null, in_use: 'Y', code_index: 2, is_annual_event: false },
  { code_id: 'FLT',  code_type: 'Floating', name: '浮動支出', parent_id: null, in_use: 'Y', code_index: 3, is_annual_event: false },
  { code_id: 'INV',  code_type: 'Invest',   name: '投資',   parent_id: null, in_use: 'Y', code_index: 4, is_annual_event: false },
  { code_id: 'TRF',  code_type: 'Transfer', name: '轉帳',   parent_id: null, in_use: 'Y', code_index: 5, is_annual_event: false },
  // Sub-codes
  { code_id: 'INC_SAL',  code_type: 'Income',   name: '薪資',   parent_id: 'INC', in_use: 'Y', code_index: 1, is_annual_event: false },
  { code_id: 'INC_BNS',  code_type: 'Income',   name: '獎金',   parent_id: 'INC', in_use: 'Y', code_index: 2, is_annual_event: false },
  { code_id: 'FIX_RNT',  code_type: 'Fixed',    name: '房租',   parent_id: 'FIX', in_use: 'Y', code_index: 1, is_annual_event: false },
  { code_id: 'FIX_UTL',  code_type: 'Fixed',    name: '水電',   parent_id: 'FIX', in_use: 'Y', code_index: 2, is_annual_event: false },
  { code_id: 'FLT_FOOD', code_type: 'Floating', name: '伙食',   parent_id: 'FLT', in_use: 'Y', code_index: 1, is_annual_event: false },
  { code_id: 'FLT_TRP',  code_type: 'Floating', name: '交通',   parent_id: 'FLT', in_use: 'Y', code_index: 2, is_annual_event: false },
  { code_id: 'INV_STK',  code_type: 'Invest',   name: '股票',   parent_id: 'INV', in_use: 'Y', code_index: 1, is_annual_event: false },
  { code_id: 'TRF_TRF',  code_type: 'Transfer', name: '一般轉帳', parent_id: 'TRF', in_use: 'Y', code_index: 1, is_annual_event: false },
]

function buildCodesTree(): CodeDataWithSub[] {
  return codes
    .filter((c) => !c.parent_id)
    .map((p) => ({ ...p, sub_codes: codes.filter((c) => c.parent_id === p.code_id) }))
}

// ─── Credit cards ────────────────────────────────────────────────────────────

let creditCards: CreditCard[] = [
  { credit_card_id: 'CC_VISA',   card_name: 'Visa 御璽', card_no: '4111-XXXX-XXXX-1234', last_day: 15, charge_day: 5,  limit_date: 0, feedback_way: 'cashback',  fx_code: 'TWD', in_use: 'Y', credit_card_index: 1, note: null },
  { credit_card_id: 'CC_MC',     card_name: 'MasterCard 鈦金', card_no: '5500-XXXX-XXXX-5678', last_day: 20, charge_day: 10, limit_date: 0, feedback_way: 'mileage', fx_code: 'TWD', in_use: 'Y', credit_card_index: 2, note: '主力卡' },
  { credit_card_id: 'CC_AMEX',   card_name: 'Amex Gold',  card_no: '3777-XXXXXX-12345', last_day: 25, charge_day: 15, limit_date: 0, feedback_way: 'points',  fx_code: 'USD', in_use: 'Y', credit_card_index: 3, note: null },
  { credit_card_id: 'CC_OLD',    card_name: '舊卡（停用）', card_no: null, last_day: null, charge_day: null, limit_date: null, feedback_way: null, fx_code: 'TWD', in_use: 'N', credit_card_index: 4, note: null },
]

// ─── Stock categories (allocation dictionary) ────────────────────────────────

let stockCategories: StockCategory[] = [
  { category_id: 'SC-001', name: '成長型', in_use: 'Y', category_index: 1 },
  { category_id: 'SC-002', name: '債券',   in_use: 'Y', category_index: 2 },
  { category_id: 'SC-003', name: '類現金', in_use: 'Y', category_index: 3 },
]
let stockCategorySeq = stockCategories.length

// ─── Budgets ─────────────────────────────────────────────────────────────────
//
// Mirrors the real backend: budgets are keyed by *main* code (parent_id IS NULL)
// and the suggest endpoint only emits Fixed/Floating categories (the
// _BUDGET_TRIGGER_TYPES in setting_service.suggest_budget). Income / Invest /
// Transfer never appear in the budget table.

const BASE_MONTHLY: Record<string, number> = { FIX: 21000, FLT: 15000 }
const BASE_ANNUAL: Record<string, number> = { FIX: 60000, FLT: 50000 }

function budgetMains(): CodeData[] {
  return codes.filter((c) => !c.parent_id && (c.code_type === 'Fixed' || c.code_type === 'Floating'))
}

function makeYearBudgets(year: string): Budget[] {
  return budgetMains().map((c) => {
    const isEvent = !!c.is_annual_event
    const monthly = isEvent ? 0 : BASE_MONTHLY[c.code_id] ?? 0
    return {
      budget_year: year,
      category_code: c.code_id,
      category_name: c.name,
      code_type: c.code_type,
      expected01: monthly, expected02: monthly, expected03: monthly,
      expected04: monthly, expected05: monthly, expected06: monthly,
      expected07: monthly, expected08: monthly, expected09: monthly,
      expected10: monthly, expected11: monthly, expected12: monthly,
      annual_amount: isEvent ? BASE_ANNUAL[c.code_id] ?? 0 : null,
    }
  })
}

let budgetsByYear: Record<string, Budget[]> = {
  '2024': makeYearBudgets('2024'),
  '2025': makeYearBudgets('2025'),
  '2026': makeYearBudgets('2026'),
}

// ─── Alarms ──────────────────────────────────────────────────────────────────

let alarms: Alarm[] = [
  { alarm_id: 1, alarm_type: 'M', alarm_date: '10', content: '繳房租', due_date: null },
  { alarm_id: 2, alarm_type: 'M', alarm_date: '20', content: 'Visa 帳單', due_date: null },
  { alarm_id: 3, alarm_type: 'Y', alarm_date: '0601', content: '綜所稅', due_date: null },
  { alarm_id: 4, alarm_type: 'Y', alarm_date: '0512', content: '每年保單檢視', due_date: null },
]
let alarmSeq = alarms.length

// ─── Handlers ────────────────────────────────────────────────────────────────

export const settingsHandlers = [
  // Accounts
  http.get('*/settings/accounts', () => ok(accounts)),
  http.post('*/settings/accounts', async ({ request }) => {
    const body = (await request.json()) as AccountCreate
    accountSeq += 1
    const created: Account = {
      id: accountSeq,
      account_id: body.account_id,
      name: body.name,
      account_type: body.account_type,
      fx_code: body.fx_code,
      is_calculate: body.is_calculate ?? 'Y',
      in_use: body.in_use ?? 'Y',
      discount: body.discount ?? 1,
      memo: body.memo ?? null,
      owner: body.owner ?? null,
      account_index: body.account_index ?? accounts.length + 1,
    }
    accounts.push(created)
    return ok(created)
  }),
  http.put('*/settings/accounts/:id', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as AccountUpdate
    const idx = accounts.findIndex((a) => a.id === id)
    const cur = accounts[idx]
    if (!cur) return fail('account not found', 404)
    const next: Account = { ...cur, ...body }
    accounts[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/accounts/:id', ({ params }) => {
    const id = Number(params.id)
    const before = accounts.length
    accounts = accounts.filter((a) => a.id !== id)
    if (accounts.length === before) return fail('account not found', 404)
    return ok(null)
  }),

  // Codes — order matters: more specific routes first
  http.get('*/settings/codes/all-with-sub', () => ok(buildCodesTree())),
  http.get('*/settings/codes', () => ok(codes.filter((c) => !c.parent_id))),
  http.post('*/settings/codes', async ({ request }) => {
    const body = (await request.json()) as CodeDataCreate
    const created: CodeData = {
      code_id: body.code_id,
      code_type: body.code_type,
      name: body.name,
      parent_id: body.parent_id ?? null,
      in_use: body.in_use ?? 'Y',
      code_index: body.code_index ?? codes.length + 1,
      is_annual_event: body.is_annual_event ?? false,
    }
    codes.push(created)
    return ok(created)
  }),
  http.put('*/settings/codes/:id', async ({ params, request }) => {
    const body = (await request.json()) as CodeDataUpdate
    const idx = codes.findIndex((c) => c.code_id === params.id)
    const cur = codes[idx]
    if (!cur) return fail('code not found', 404)
    const next: CodeData = { ...cur, ...body }
    codes[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/codes/:id', ({ params }) => {
    const before = codes.length
    codes = codes.filter((c) => c.code_id !== params.id)
    if (codes.length === before) return fail('code not found', 404)
    return ok(null)
  }),

  // Sub-codes share same store; routes only mutate child rows
  http.post('*/settings/sub-codes', async ({ request }) => {
    const body = (await request.json()) as CodeDataCreate
    const created: CodeData = {
      code_id: body.code_id,
      code_type: body.code_type,
      name: body.name,
      parent_id: body.parent_id ?? null,
      in_use: body.in_use ?? 'Y',
      code_index: body.code_index ?? codes.length + 1,
      is_annual_event: body.is_annual_event ?? false,
    }
    codes.push(created)
    return ok(created)
  }),
  http.put('*/settings/sub-codes/:id', async ({ params, request }) => {
    const body = (await request.json()) as CodeDataUpdate
    const idx = codes.findIndex((c) => c.code_id === params.id)
    const cur = codes[idx]
    if (!cur) return fail('sub-code not found', 404)
    const next: CodeData = { ...cur, ...body }
    codes[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/sub-codes/:id', ({ params }) => {
    const before = codes.length
    codes = codes.filter((c) => c.code_id !== params.id)
    if (codes.length === before) return fail('sub-code not found', 404)
    return ok(null)
  }),

  // Credit cards
  http.get('*/settings/credit-cards', () => ok(creditCards)),
  http.post('*/settings/credit-cards', async ({ request }) => {
    const body = (await request.json()) as CreditCardCreate
    const created: CreditCard = {
      credit_card_id: body.credit_card_id,
      card_name: body.card_name,
      card_no: body.card_no ?? null,
      last_day: body.last_day ?? null,
      charge_day: body.charge_day ?? null,
      limit_date: body.limit_date ?? null,
      feedback_way: body.feedback_way ?? null,
      fx_code: body.fx_code,
      in_use: body.in_use ?? 'Y',
      credit_card_index: body.credit_card_index ?? creditCards.length + 1,
      note: body.note ?? null,
    }
    creditCards.push(created)
    return ok(created)
  }),
  http.put('*/settings/credit-cards/:id', async ({ params, request }) => {
    const body = (await request.json()) as CreditCardUpdate
    const idx = creditCards.findIndex((c) => c.credit_card_id === params.id)
    const cur = creditCards[idx]
    if (!cur) return fail('card not found', 404)
    const next: CreditCard = { ...cur, ...body }
    creditCards[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/credit-cards/:id', ({ params }) => {
    const before = creditCards.length
    creditCards = creditCards.filter((c) => c.credit_card_id !== params.id)
    if (creditCards.length === before) return fail('card not found', 404)
    return ok(null)
  }),

  // Stock categories
  http.get('*/settings/stock-categories', () =>
    ok([...stockCategories].sort((a, b) => a.category_index - b.category_index)),
  ),
  http.post('*/settings/stock-categories', async ({ request }) => {
    const body = (await request.json()) as StockCategoryCreate
    stockCategorySeq += 1
    const created: StockCategory = {
      category_id: `SC-${String(stockCategorySeq).padStart(3, '0')}`,
      name: body.name,
      in_use: body.in_use ?? 'Y',
      category_index: body.category_index ?? stockCategories.length + 1,
    }
    stockCategories.push(created)
    return ok(created)
  }),
  http.put('*/settings/stock-categories/:id', async ({ params, request }) => {
    const body = (await request.json()) as StockCategoryUpdate
    const idx = stockCategories.findIndex((c) => c.category_id === params.id)
    const cur = stockCategories[idx]
    if (!cur) return fail('stock category not found', 404)
    const next: StockCategory = { ...cur, ...body }
    stockCategories[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/stock-categories/:id', ({ params }) => {
    const before = stockCategories.length
    stockCategories = stockCategories.filter((c) => c.category_id !== params.id)
    if (stockCategories.length === before) return fail('stock category not found', 404)
    return ok(null)
  }),

  // Budgets — specific routes before generic
  http.get('*/settings/budgets/year-range', () => {
    const years = Object.keys(budgetsByYear).sort()
    return ok(years)
  }),
  http.post('*/settings/budgets/:year/suggest', ({ params }) => {
    const year = String(params.year)
    // Re-derive the suggestion from current main codes so toggling
    // is_annual_event in 選單設定 is reflected immediately in the preview.
    return ok(makeYearBudgets(year))
  }),
  http.post('*/settings/budgets/:year/apply', async ({ params, request }) => {
    const year = String(params.year)
    const body = (await request.json()) as Budget[]
    budgetsByYear[year] = body.map((b) => ({ ...b, budget_year: year }))
    return ok(budgetsByYear[year])
  }),
  http.get('*/settings/budgets/:year', ({ params }) => {
    const year = String(params.year)
    if (!budgetsByYear[year]) budgetsByYear[year] = makeYearBudgets(year)
    return ok(budgetsByYear[year])
  }),
  http.put('*/settings/budgets', async ({ request }) => {
    const body = (await request.json()) as Budget[]
    if (!Array.isArray(body) || body.length === 0 || !body[0]) return fail('empty payload')
    const year = body[0].budget_year
    const next = body.map((b) => ({ ...b }))
    budgetsByYear[year] = next
    return ok(next)
  }),

  // Alarms
  http.get('*/settings/alarms/by-date', ({ request }) => {
    const url = new URL(request.url)
    const start = url.searchParams.get('start') ?? '00000000'
    const end = url.searchParams.get('end') ?? '99999999'
    return ok(alarms.filter((a) => a.alarm_date >= start && a.alarm_date <= end))
  }),
  http.get('*/settings/alarms', () => ok(alarms)),
  http.post('*/settings/alarms', async ({ request }) => {
    const body = (await request.json()) as AlarmCreate
    alarmSeq += 1
    const created: Alarm = {
      alarm_id: alarmSeq,
      alarm_type: body.alarm_type,
      alarm_date: body.alarm_date,
      content: body.content,
      due_date: body.due_date ?? null,
    }
    alarms.push(created)
    return ok(created)
  }),
  http.put('*/settings/alarms/:id', async ({ params, request }) => {
    const id = Number(params.id)
    const body = (await request.json()) as AlarmUpdate
    const idx = alarms.findIndex((a) => a.alarm_id === id)
    const cur = alarms[idx]
    if (!cur) return fail('alarm not found', 404)
    const next: Alarm = { ...cur, ...body }
    alarms[idx] = next
    return ok(next)
  }),
  http.delete('*/settings/alarms/:id', ({ params }) => {
    const id = Number(params.id)
    const before = alarms.length
    alarms = alarms.filter((a) => a.alarm_id !== id)
    if (alarms.length === before) return fail('alarm not found', 404)
    return ok(null)
  }),
]

// Read-only accessors for cross-handler reuse (utilities/dashboard mocks)
export function _accountsSnapshot() { return accounts }
export function _codesSnapshot() { return codes }
export function _creditCardsSnapshot() { return creditCards }
export function _alarmsSnapshot() { return alarms }
export function _budgetsForYear(year: string) {
  if (!budgetsByYear[year]) budgetsByYear[year] = makeYearBudgets(year)
  return budgetsByYear[year]
}
