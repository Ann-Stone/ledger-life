import { http } from 'msw'
import { ok, fail } from '../util'
import type {
  EstateAsset,
  EstateAssetCreate,
  EstateAssetUpdate,
  EstateJournal,
  EstateJournalCreate,
  EstateJournalUpdate,
  InsuranceAsset,
  InsuranceAssetCreate,
  InsuranceAssetUpdate,
  InsuranceJournal,
  InsuranceJournalCreate,
  InsuranceJournalUpdate,
  LoanAsset,
  LoanAssetCreate,
  LoanAssetUpdate,
  LoanJournal,
  LoanJournalCreate,
  LoanJournalUpdate,
  LoanSelection,
  OtherAsset,
  OtherAssetCreate,
  OtherAssetItem,
  OtherAssetUpdate,
  StockAsset,
  StockAssetCreate,
  StockAssetUpdate,
  StockJournal,
  StockJournalCreate,
  StockJournalUpdate,
  StockPnlSummary,
} from '@/types/models'

// ─── Stocks ──────────────────────────────────────────────────────────────────

let stocks: StockAsset[] = [
  { stock_id: 'STK_0050', stock_code: '0050', stock_name: '元大台灣 50',     asset_id: 'STK', expected_spend: 200000, category_id: 'SC-001' },
  { stock_id: 'STK_2330', stock_code: '2330', stock_name: '台積電',         asset_id: 'STK', expected_spend: 500000, category_id: 'SC-001' },
  { stock_id: 'STK_VOO',  stock_code: 'VOO',  stock_name: 'Vanguard S&P500', asset_id: 'STK_US', expected_spend: 300000, category_id: 'SC-002' },
]

export const _stocksSnapshot = (): readonly StockAsset[] => stocks

// excute_price is the whole-transaction cash amount (fees included), not a
// per-share price: buy 1000 of 0050 cost 165,000; the cash dividend row records
// the 4,500 total received (shares = 0); the stock dividend adds 1 free share.
let stockJournals: StockJournal[] = [
  { distinct_number: 1, stock_id: 'STK_0050', excute_type: 'buy',   excute_amount: 1000, excute_price: 165000, excute_date: '20260105', account_id: 'BANK_CTBC', account_name: '中信活存', memo: '年初加碼' },
  { distinct_number: 2, stock_id: 'STK_0050', excute_type: 'cash',  excute_amount: 0,    excute_price: 4500,   excute_date: '20260315', account_id: 'BANK_CTBC', account_name: '中信活存', memo: '現金股利' },
  { distinct_number: 3, stock_id: 'STK_2330', excute_type: 'buy',   excute_amount: 50,   excute_price: 42500,  excute_date: '20260210', account_id: 'BANK_CTBC', account_name: '中信活存', memo: null },
  { distinct_number: 4, stock_id: 'STK_2330', excute_type: 'sell',  excute_amount: 10,   excute_price: 9200,   excute_date: '20260418', account_id: 'BANK_CTBC', account_name: '中信活存', memo: '部分獲利了結' },
  { distinct_number: 5, stock_id: 'STK_VOO',  excute_type: 'buy',   excute_amount: 5,    excute_price: 2400,   excute_date: '20260120', account_id: 'BANK_USD',  account_name: 'Wise USD',  memo: null },
  { distinct_number: 6, stock_id: 'STK_VOO',  excute_type: 'stock', excute_amount: 1,    excute_price: 0,      excute_date: '20260301', account_id: 'BANK_USD',  account_name: 'Wise USD',  memo: '股票股利' },
]
let stockJournalSeq = stockJournals.length

// Illustrative latest close prices for the demo tickers (own currency).
const stockClosePrices: Record<string, number> = {
  '0050': 190,
  '2330': 1100,
  VOO: 530,
}
// 12 months before the app's current month (2026-06) — cash-dividend yield window.
const STOCK_TTM_CUTOFF = '20250701'

// Mirrors the backend compute_stock_pnl_summary: excute_type-driven, abs()
// magnitudes, moving-average cost, realized = price-vs-avg gains, dividends via
// cash rows; money in the holding's own currency.
export function computeStockPnlSummary(assetId: string | null): StockPnlSummary[] {
  const holdings = assetId ? stocks.filter((s) => s.asset_id === assetId) : stocks
  const round = (n: number | null, p: number): number | null =>
    n == null ? null : Math.round(n * 10 ** p) / 10 ** p
  return holdings.map((h) => {
    const rows = stockJournals
      .filter((j) => j.stock_id === h.stock_id)
      .sort((a, b) =>
        a.excute_date === b.excute_date
          ? a.distinct_number - b.distinct_number
          : a.excute_date.localeCompare(b.excute_date),
      )
    let shares = 0
    let totalCost = 0
    let realized = 0
    let dividends = 0
    let ttmDividends = 0
    let fxCode = 'TWD'
    for (const r of rows) {
      const amt = Math.abs(r.excute_amount)
      const total = Math.abs(r.excute_price) // whole-transaction amount, fees included
      if (r.account_id?.includes('USD')) fxCode = 'USD'
      if (r.excute_type === 'buy') {
        shares += amt
        totalCost += total
      } else if (r.excute_type === 'stock') {
        shares += amt
      } else if (r.excute_type === 'sell') {
        const avg = shares > 1e-6 ? totalCost / shares : 0
        const costOut = avg * amt
        realized += total - costOut
        totalCost -= costOut
        shares -= amt
      } else if (r.excute_type === 'cash') {
        dividends += total
        if (r.excute_date >= STOCK_TTM_CUTOFF) ttmDividends += total
      }
    }
    if (Math.abs(shares) < 1e-6) {
      shares = 0
      totalCost = 0
    }
    const close = stockClosePrices[h.stock_code] ?? null
    const marketValue = shares === 0 ? 0 : close != null ? shares * close : null
    const unrealized = marketValue != null ? marketValue - totalCost : null
    const unrealizedPct =
      unrealized != null && totalCost > 1e-6 ? unrealized / totalCost : null
    const cashYield =
      marketValue != null && marketValue !== 0 ? ttmDividends / marketValue : null
    const costYield = totalCost > 1e-6 ? dividends / totalCost : null
    return {
      stock_id: h.stock_id,
      stock_code: h.stock_code,
      stock_name: h.stock_name,
      shares: round(shares, 6)!,
      cost: round(totalCost, 2)!,
      market_value: round(marketValue, 2),
      realized: round(realized, 2)!,
      dividends_total: round(dividends, 2)!,
      unrealized: round(unrealized, 2),
      unrealized_pct: round(unrealizedPct, 6),
      cash_yield: round(cashYield, 6),
      cost_yield: round(costYield, 6),
      fx_code: fxCode,
      close_price: close,
      price_date: close != null ? '20260619' : null,
    }
  })
}

// ─── Estates ─────────────────────────────────────────────────────────────────

let estates: EstateAsset[] = [
  { estate_id: 'EST_HOME',  estate_name: '主要住所',     estate_type: 'house',   estate_address: '台北市信義區', asset_id: 'EST', fx_code: 'TWD', obtain_date: '20200815', loan_id: 'LN_HOUSE', estate_status: 'live', region: '臺北市', memo: '自住' },
  { estate_id: 'EST_INV',   estate_name: '投資宅 A',     estate_type: 'apartment', estate_address: '新北市板橋區', asset_id: 'EST', fx_code: 'TWD', obtain_date: '20221201', loan_id: null,       estate_status: 'rent', region: '新北市', memo: '長期出租' },
  { estate_id: 'EST_OLD',   estate_name: '舊宅（已售）',  estate_type: 'house',   estate_address: '桃園市',     asset_id: 'EST', fx_code: 'TWD', obtain_date: '20180501', loan_id: null,       estate_status: 'sold', memo: '2024 年出售' },
  { estate_id: 'EST_LAND',  estate_name: '空地',         estate_type: 'land',    estate_address: '宜蘭',       asset_id: 'EST', fx_code: 'TWD', obtain_date: '20210601', loan_id: null,       estate_status: 'idle', memo: null },
]

let estateJournals: EstateJournal[] = [
  { distinct_number: 1, estate_id: 'EST_HOME', estate_excute_type: 'tax',       excute_price: 12000, excute_date: '20260301', memo: '房屋稅' },
  { distinct_number: 2, estate_id: 'EST_HOME', estate_excute_type: 'fee',       excute_price: 3000,  excute_date: '20260401', memo: '管理費' },
  { distinct_number: 3, estate_id: 'EST_HOME', estate_excute_type: 'fix',       excute_price: 8500,  excute_date: '20260415', memo: '冷氣維修' },
  { distinct_number: 4, estate_id: 'EST_INV',  estate_excute_type: 'rent',      excute_price: 25000, excute_date: '20260405', memo: '4 月租金' },
  { distinct_number: 5, estate_id: 'EST_INV',  estate_excute_type: 'deposit',   excute_price: 50000, excute_date: '20221201', memo: '押金' },
  { distinct_number: 6, estate_id: 'EST_INV',  estate_excute_type: 'insurance', excute_price: 4200,  excute_date: '20260201', memo: '住宅險' },
]
let estateJournalSeq = estateJournals.length

// ─── Insurances ──────────────────────────────────────────────────────────────

let insurances: InsuranceAsset[] = [
  { insurance_id: 'INS_LIFE',    insurance_name: '終身壽險',  asset_id: 'INS', in_account: 'BANK_CTBC', out_account: 'BANK_CTBC', start_date: '20180101', end_date: '20480101', pay_type: 'monthly', pay_day: '5',  expected_spend: 5000,  has_closed: 'N' },
  { insurance_id: 'INS_HEALTH',  insurance_name: '醫療險',    asset_id: 'INS', in_account: 'BANK_CTBC', out_account: 'BANK_CTBC', start_date: '20210101', end_date: '20510101', pay_type: 'yearly',  pay_day: '1',  expected_spend: 24000, has_closed: 'N' },
  { insurance_id: 'INS_OLD',     insurance_name: '舊保單（已結清）', asset_id: 'INS', in_account: 'BANK_CTBC', out_account: 'BANK_CTBC', start_date: '20100101', end_date: '20240101', pay_type: 'monthly', pay_day: '10', expected_spend: 0,     has_closed: 'Y' },
]

let insuranceJournals: InsuranceJournal[] = [
  { distinct_number: 1, insurance_id: 'INS_LIFE',   insurance_excute_type: 'pay',    excute_price: 5000,  excute_date: '20260405', memo: '4 月保費' },
  { distinct_number: 2, insurance_id: 'INS_LIFE',   insurance_excute_type: 'expect', excute_price: 60000, excute_date: '20260101', memo: '年度預算' },
  { distinct_number: 3, insurance_id: 'INS_HEALTH', insurance_excute_type: 'pay',    excute_price: 24000, excute_date: '20260101', memo: '一次年繳' },
  { distinct_number: 4, insurance_id: 'INS_OLD',    insurance_excute_type: 'cash',   excute_price: 35000, excute_date: '20240101', memo: '結清退款' },
]
let insuranceJournalSeq = insuranceJournals.length

// ─── Loans ───────────────────────────────────────────────────────────────────

let loans: LoanAsset[] = [
  { loan_id: 'LN_HOUSE',     loan_name: '房貸主貸',  loan_type: 'mortgage', account_id: 'BANK_CTBC', account_name: '中信活存', interest_rate: 0.0205, period: 360, apply_date: '20200815', grace_expire_date: '20230815', pay_day: 10, amount: 8000000, repayed: 1200000, loan_index: 1 },
  { loan_id: 'LN_CAR',       loan_name: '車貸',     loan_type: 'auto',     account_id: 'BANK_CTBC', account_name: '中信活存', interest_rate: 0.0388, period: 60,  apply_date: '20240301', grace_expire_date: null,        pay_day: 15, amount: 800000,  repayed: 320000,  loan_index: 2 },
  { loan_id: 'LN_PERSONAL',  loan_name: '信貸',     loan_type: 'personal', account_id: 'BANK_CTBC', account_name: '中信活存', interest_rate: 0.05,   period: 36,  apply_date: '20250115', grace_expire_date: null,        pay_day: 20, amount: 500000,  repayed: 100000,  loan_index: 3 },
]

let loanJournals: LoanJournal[] = [
  { distinct_number: 1, loan_id: 'LN_HOUSE', loan_excute_type: 'principal', excute_price: 18000, excute_date: '20260410', memo: '4 月本金' },
  { distinct_number: 2, loan_id: 'LN_HOUSE', loan_excute_type: 'interest',  excute_price: 13680, excute_date: '20260410', memo: '4 月利息' },
  { distinct_number: 3, loan_id: 'LN_HOUSE', loan_excute_type: 'principal', excute_price: 18000, excute_date: '20260310', memo: '3 月本金' },
  { distinct_number: 4, loan_id: 'LN_HOUSE', loan_excute_type: 'interest',  excute_price: 13700, excute_date: '20260310', memo: '3 月利息' },
  { distinct_number: 5, loan_id: 'LN_CAR',   loan_excute_type: 'principal', excute_price: 13333, excute_date: '20260415', memo: null },
  { distinct_number: 6, loan_id: 'LN_CAR',   loan_excute_type: 'interest',  excute_price: 1900,  excute_date: '20260415', memo: null },
  { distinct_number: 7, loan_id: 'LN_HOUSE', loan_excute_type: 'fee',       excute_price: 1500,  excute_date: '20260101', memo: '帳管費' },
]
let loanJournalSeq = loanJournals.length

// ─── Other assets ────────────────────────────────────────────────────────────

let otherAssets: OtherAsset[] = [
  { asset_id: 'CASH',    asset_name: '現金',     asset_type: 'cash',     in_use: 'Y', asset_index: 1 },
  { asset_id: 'STK',     asset_name: '台股',     asset_type: 'stock',    in_use: 'Y', asset_index: 2 },
  { asset_id: 'STK_US',  asset_name: '美股',     asset_type: 'stock',    in_use: 'Y', asset_index: 3 },
  { asset_id: 'EST',     asset_name: '不動產',   asset_type: 'estate',   in_use: 'Y', asset_index: 4 },
  { asset_id: 'INS',     asset_name: '保單',     asset_type: 'insurance', in_use: 'Y', asset_index: 5 },
  { asset_id: 'CRYPTO',  asset_name: '加密貨幣', asset_type: 'crypto',   in_use: 'Y', asset_index: 6 },
  { asset_id: 'OLD_BOND', asset_name: '舊債券（停用）', asset_type: 'bond', in_use: 'N', asset_index: 7 },
]

// ─── Loan selection ──────────────────────────────────────────────────────────

function loanSelection(): LoanSelection[] {
  return loans.map((l) => ({ loan_id: l.loan_id, loan_name: l.loan_name }))
}

function recomputeRepayed(loanId: string) {
  const li = loans.findIndex((l) => l.loan_id === loanId)
  const cur = loans[li]
  if (!cur) return
  const repayed = loanJournals
    .filter((j) => j.loan_id === loanId && j.loan_excute_type === 'principal')
    .reduce((s, j) => s + j.excute_price, 0)
  loans[li] = { ...cur, repayed }
}

// ─── Handlers ────────────────────────────────────────────────────────────────

export const assetsHandlers = [
  // Stocks — list + CRUD
  http.get('*/assets/stocks/summary', ({ request }) => {
    const url = new URL(request.url)
    return ok(computeStockPnlSummary(url.searchParams.get('asset_id')))
  }),
  http.get('*/assets/stocks/:id/details', ({ params }) =>
    ok(stockJournals.filter((j) => j.stock_id === String(params.id))),
  ),
  http.post('*/assets/stocks/:id/details', async ({ params, request }) => {
    const body = (await request.json()) as StockJournalCreate
    stockJournalSeq += 1
    const created: StockJournal = {
      distinct_number: stockJournalSeq,
      stock_id: String(params.id),
      excute_type: body.excute_type,
      excute_amount: body.excute_amount,
      excute_price: body.excute_price,
      excute_date: body.excute_date,
      account_id: body.account_id,
      account_name: body.account_name,
      memo: body.memo ?? null,
    }
    stockJournals.push(created)
    return ok(created)
  }),
  http.put('*/assets/stocks/details/:dn', async ({ params, request }) => {
    const dn = Number(params.dn)
    const body = (await request.json()) as StockJournalUpdate
    const idx = stockJournals.findIndex((j) => j.distinct_number === dn)
    const cur = stockJournals[idx]
    if (!cur) return fail('stock detail not found', 404)
    const next: StockJournal = { ...cur, ...body }
    stockJournals[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/stocks/details/:dn', ({ params }) => {
    const dn = Number(params.dn)
    const before = stockJournals.length
    stockJournals = stockJournals.filter((j) => j.distinct_number !== dn)
    if (stockJournals.length === before) return fail('stock detail not found', 404)
    return ok(null)
  }),
  http.get('*/assets/stocks', ({ request }) => {
    const url = new URL(request.url)
    const assetId = url.searchParams.get('asset_id')
    const filtered = assetId ? stocks.filter((s) => s.asset_id === assetId) : stocks
    return ok(filtered)
  }),
  http.post('*/assets/stocks', async ({ request }) => {
    const body = (await request.json()) as StockAssetCreate
    const created: StockAsset = { ...body }
    stocks.push(created)
    return ok(created)
  }),
  http.put('*/assets/stocks/:id', async ({ params, request }) => {
    const body = (await request.json()) as StockAssetUpdate
    const idx = stocks.findIndex((s) => s.stock_id === String(params.id))
    const cur = stocks[idx]
    if (!cur) return fail('stock not found', 404)
    const next: StockAsset = { ...cur, ...body }
    stocks[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/stocks/:id', ({ params }) => {
    const before = stocks.length
    stocks = stocks.filter((s) => s.stock_id !== String(params.id))
    if (stocks.length === before) return fail('stock not found', 404)
    return ok(null)
  }),

  // Estates
  http.get('*/assets/estates/:id/details', ({ params }) =>
    ok(estateJournals.filter((j) => j.estate_id === String(params.id))),
  ),
  http.post('*/assets/estates/:id/details', async ({ params, request }) => {
    const body = (await request.json()) as EstateJournalCreate
    estateJournalSeq += 1
    const created: EstateJournal = {
      distinct_number: estateJournalSeq,
      estate_id: String(params.id),
      estate_excute_type: body.estate_excute_type,
      excute_price: body.excute_price,
      excute_date: body.excute_date,
      memo: body.memo ?? null,
    }
    estateJournals.push(created)
    return ok(created)
  }),
  http.put('*/assets/estates/details/:dn', async ({ params, request }) => {
    const dn = Number(params.dn)
    const body = (await request.json()) as EstateJournalUpdate
    const idx = estateJournals.findIndex((j) => j.distinct_number === dn)
    const cur = estateJournals[idx]
    if (!cur) return fail('estate detail not found', 404)
    const next: EstateJournal = { ...cur, ...body }
    estateJournals[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/estates/details/:dn', ({ params }) => {
    const dn = Number(params.dn)
    const before = estateJournals.length
    estateJournals = estateJournals.filter((j) => j.distinct_number !== dn)
    if (estateJournals.length === before) return fail('estate detail not found', 404)
    return ok(null)
  }),
  http.get('*/assets/estates', ({ request }) => {
    const url = new URL(request.url)
    const assetId = url.searchParams.get('asset_id')
    const filtered = assetId ? estates.filter((e) => e.asset_id === assetId) : estates
    return ok(filtered)
  }),
  http.post('*/assets/estates', async ({ request }) => {
    const body = (await request.json()) as EstateAssetCreate
    const created: EstateAsset = {
      estate_id: body.estate_id,
      estate_name: body.estate_name,
      estate_type: body.estate_type,
      estate_address: body.estate_address,
      asset_id: body.asset_id,
      fx_code: body.fx_code ?? 'TWD',
      obtain_date: body.obtain_date,
      loan_id: body.loan_id ?? null,
      estate_status: body.estate_status,
      region: body.region ?? null,
      memo: body.memo ?? null,
    }
    estates.push(created)
    return ok(created)
  }),
  http.put('*/assets/estates/:id', async ({ params, request }) => {
    const body = (await request.json()) as EstateAssetUpdate
    const idx = estates.findIndex((e) => e.estate_id === String(params.id))
    const cur = estates[idx]
    if (!cur) return fail('estate not found', 404)
    const next: EstateAsset = { ...cur, ...body }
    estates[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/estates/:id', ({ params }) => {
    const before = estates.length
    estates = estates.filter((e) => e.estate_id !== String(params.id))
    if (estates.length === before) return fail('estate not found', 404)
    return ok(null)
  }),

  // Insurances
  http.get('*/assets/insurances/:id/details', ({ params }) =>
    ok(insuranceJournals.filter((j) => j.insurance_id === String(params.id))),
  ),
  http.post('*/assets/insurances/:id/details', async ({ params, request }) => {
    const body = (await request.json()) as InsuranceJournalCreate
    insuranceJournalSeq += 1
    const created: InsuranceJournal = {
      distinct_number: insuranceJournalSeq,
      insurance_id: String(params.id),
      insurance_excute_type: body.insurance_excute_type,
      excute_price: body.excute_price,
      excute_date: body.excute_date,
      memo: body.memo ?? null,
    }
    insuranceJournals.push(created)
    return ok(created)
  }),
  http.put('*/assets/insurances/details/:dn', async ({ params, request }) => {
    const dn = Number(params.dn)
    const body = (await request.json()) as InsuranceJournalUpdate
    const idx = insuranceJournals.findIndex((j) => j.distinct_number === dn)
    const cur = insuranceJournals[idx]
    if (!cur) return fail('insurance detail not found', 404)
    const next: InsuranceJournal = { ...cur, ...body }
    insuranceJournals[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/insurances/details/:dn', ({ params }) => {
    const dn = Number(params.dn)
    const before = insuranceJournals.length
    insuranceJournals = insuranceJournals.filter((j) => j.distinct_number !== dn)
    if (insuranceJournals.length === before) return fail('insurance detail not found', 404)
    return ok(null)
  }),
  http.get('*/assets/insurances', ({ request }) => {
    const url = new URL(request.url)
    const assetId = url.searchParams.get('asset_id')
    const filtered = assetId ? insurances.filter((i) => i.asset_id === assetId) : insurances
    return ok(filtered)
  }),
  http.post('*/assets/insurances', async ({ request }) => {
    const body = (await request.json()) as InsuranceAssetCreate
    insurances.push({ ...body })
    return ok(body)
  }),
  http.put('*/assets/insurances/:id', async ({ params, request }) => {
    const body = (await request.json()) as InsuranceAssetUpdate
    const idx = insurances.findIndex((i) => i.insurance_id === String(params.id))
    const cur = insurances[idx]
    if (!cur) return fail('insurance not found', 404)
    const next: InsuranceAsset = { ...cur, ...body }
    insurances[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/insurances/:id', ({ params }) => {
    const before = insurances.length
    insurances = insurances.filter((i) => i.insurance_id !== String(params.id))
    if (insurances.length === before) return fail('insurance not found', 404)
    return ok(null)
  }),

  // Loans — selection first, then details, then specific id, then list
  http.get('*/assets/loans/selection', () => ok(loanSelection())),
  http.get('*/assets/loans/:id/details', ({ params }) =>
    ok(loanJournals.filter((j) => j.loan_id === String(params.id))),
  ),
  http.post('*/assets/loans/:id/details', async ({ params, request }) => {
    const body = (await request.json()) as LoanJournalCreate
    loanJournalSeq += 1
    const created: LoanJournal = {
      distinct_number: loanJournalSeq,
      loan_id: String(params.id),
      loan_excute_type: body.loan_excute_type,
      excute_price: body.excute_price,
      excute_date: body.excute_date,
      memo: body.memo ?? null,
    }
    loanJournals.push(created)
    recomputeRepayed(created.loan_id)
    return ok(created)
  }),
  http.put('*/assets/loans/details/:dn', async ({ params, request }) => {
    const dn = Number(params.dn)
    const body = (await request.json()) as LoanJournalUpdate
    const idx = loanJournals.findIndex((j) => j.distinct_number === dn)
    const cur = loanJournals[idx]
    if (!cur) return fail('loan detail not found', 404)
    const next: LoanJournal = { ...cur, ...body }
    loanJournals[idx] = next
    recomputeRepayed(next.loan_id)
    return ok(next)
  }),
  http.delete('*/assets/loans/details/:dn', ({ params }) => {
    const dn = Number(params.dn)
    const target = loanJournals.find((j) => j.distinct_number === dn)
    if (!target) return fail('loan detail not found', 404)
    loanJournals = loanJournals.filter((j) => j.distinct_number !== dn)
    recomputeRepayed(target.loan_id)
    return ok(null)
  }),
  http.get('*/assets/loans/:id', ({ params }) => {
    const found = loans.find((l) => l.loan_id === String(params.id))
    if (!found) return fail('loan not found', 404)
    return ok(found)
  }),
  http.get('*/assets/loans', () => ok(loans)),
  http.post('*/assets/loans', async ({ request }) => {
    const body = (await request.json()) as LoanAssetCreate
    loans.push({ ...body })
    return ok(body)
  }),
  http.put('*/assets/loans/:id', async ({ params, request }) => {
    const body = (await request.json()) as LoanAssetUpdate
    const idx = loans.findIndex((l) => l.loan_id === String(params.id))
    const cur = loans[idx]
    if (!cur) return fail('loan not found', 404)
    const next: LoanAsset = { ...cur, ...body }
    loans[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/loans/:id', ({ params }) => {
    const before = loans.length
    loans = loans.filter((l) => l.loan_id !== String(params.id))
    if (loans.length === before) return fail('loan not found', 404)
    return ok(null)
  }),

  // Other assets — items list + flat CRUD
  http.get('*/assets/other-assets/items', () => {
    const seen = new Set<string>()
    const items: OtherAssetItem[] = []
    for (const a of otherAssets) {
      if (!seen.has(a.asset_type)) { seen.add(a.asset_type); items.push({ asset_type: a.asset_type }) }
    }
    return ok(items)
  }),
  http.get('*/assets/other-assets', () => ok(otherAssets)),
  http.post('*/assets/other-assets', async ({ request }) => {
    const body = (await request.json()) as OtherAssetCreate
    const created: OtherAsset = {
      asset_id: body.asset_id,
      asset_name: body.asset_name,
      asset_type: body.asset_type,
      in_use: body.in_use,
      asset_index: body.asset_index ?? Math.max(0, ...otherAssets.map((a) => a.asset_index)) + 1,
    }
    otherAssets.push(created)
    return ok(created)
  }),
  http.put('*/assets/other-assets/:id', async ({ params, request }) => {
    const body = (await request.json()) as OtherAssetUpdate
    const idx = otherAssets.findIndex((a) => a.asset_id === String(params.id))
    const cur = otherAssets[idx]
    if (!cur) return fail('other asset not found', 404)
    const next: OtherAsset = { ...cur, ...body }
    otherAssets[idx] = next
    return ok(next)
  }),
  http.delete('*/assets/other-assets/:id', ({ params }) => {
    const before = otherAssets.length
    otherAssets = otherAssets.filter((a) => a.asset_id !== String(params.id))
    if (otherAssets.length === before) return fail('other asset not found', 404)
    return ok(null)
  }),
]
