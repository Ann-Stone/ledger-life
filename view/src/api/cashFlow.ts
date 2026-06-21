import request from '@/utils/request'
import type {
  Journal,
  JournalCreate,
  JournalUpdate,
  JournalListResponse,
  JournalExpenditureBudget,
  JournalExpenditureRatio,
  JournalInvestRatio,
  JournalLiability,
  JournalEstateTransactionCreate,
  JournalEstateTransactionRead,
  JournalEstateTransactionUpdate,
  JournalInsuranceTransactionCreate,
  JournalInsuranceTransactionRead,
  JournalInsuranceTransactionUpdate,
  JournalLoanTransactionCreate,
  JournalLoanTransactionRead,
  JournalLoanTransactionUpdate,
  JournalStockTransactionCreate,
  JournalStockTransactionRead,
  JournalStockTransactionUpdate,
  SettleResult,
  StockPriceEntry,
  StockPriceHistory,
  InsuranceValueMonth,
  InsuranceValueCreate,
  EstateValueMonth,
  EstateValueCreate,
  EstateValueSuggestion,
  IndexRefreshResult,
  UncategorizedSummary,
} from '@/types/models'

// ─── Journals ────────────────────────────────────────────────────────────────

export function getJournals(vestingMonth: string): Promise<JournalListResponse> {
  return request.get(`/monthly-report/journals/${vestingMonth}`)
}

export function getUncategorizedSummary(): Promise<UncategorizedSummary> {
  return request.get('/monthly-report/journals/uncategorized-summary')
}

export function createJournal(data: JournalCreate): Promise<Journal> {
  return request.post('/monthly-report/journals', data)
}

export function updateJournal(id: number, data: JournalUpdate): Promise<Journal> {
  return request.put(`/monthly-report/journals/${id}`, data)
}

export function deleteJournal(id: number): Promise<null> {
  return request.delete(`/monthly-report/journals/${id}`)
}

export function createJournalWithStockTransaction(
  data: JournalStockTransactionCreate,
): Promise<JournalStockTransactionRead> {
  return request.post('/monthly-report/journals/stock-transaction', data)
}

export function updateJournalWithStockTransaction(
  id: number,
  data: JournalStockTransactionUpdate,
): Promise<JournalStockTransactionRead> {
  return request.put(`/monthly-report/journals/${id}/stock-transaction`, data)
}

export function createJournalWithInsuranceTransaction(
  data: JournalInsuranceTransactionCreate,
): Promise<JournalInsuranceTransactionRead> {
  return request.post('/monthly-report/journals/insurance-transaction', data)
}

export function updateJournalWithInsuranceTransaction(
  id: number,
  data: JournalInsuranceTransactionUpdate,
): Promise<JournalInsuranceTransactionRead> {
  return request.put(`/monthly-report/journals/${id}/insurance-transaction`, data)
}

export function createJournalWithEstateTransaction(
  data: JournalEstateTransactionCreate,
): Promise<JournalEstateTransactionRead> {
  return request.post('/monthly-report/journals/estate-transaction', data)
}

export function updateJournalWithEstateTransaction(
  id: number,
  data: JournalEstateTransactionUpdate,
): Promise<JournalEstateTransactionRead> {
  return request.put(`/monthly-report/journals/${id}/estate-transaction`, data)
}

export function createJournalWithLoanTransaction(
  data: JournalLoanTransactionCreate,
): Promise<JournalLoanTransactionRead> {
  return request.post('/monthly-report/journals/loan-transaction', data)
}

export function updateJournalWithLoanTransaction(
  id: number,
  data: JournalLoanTransactionUpdate,
): Promise<JournalLoanTransactionRead> {
  return request.put(`/monthly-report/journals/${id}/loan-transaction`, data)
}

// ─── Analytics ───────────────────────────────────────────────────────────────

export function getExpenditureBudget(month: string): Promise<JournalExpenditureBudget> {
  return request.get(`/monthly-report/journals/${month}/expenditure-budget`)
}

export function getExpenditureRatio(month: string): Promise<JournalExpenditureRatio> {
  return request.get(`/monthly-report/journals/${month}/expenditure-ratio`)
}

export function getInvestRatio(month: string): Promise<JournalInvestRatio> {
  return request.get(`/monthly-report/journals/${month}/invest-ratio`)
}

export function getLiability(month: string): Promise<JournalLiability> {
  return request.get(`/monthly-report/journals/${month}/liability`)
}

// ─── Settle ──────────────────────────────────────────────────────────────────

export function settleMonth(vestingMonth: string): Promise<SettleResult> {
  return request.put(`/monthly-report/balance/${vestingMonth}/settle`)
}

// ─── Stock prices ────────────────────────────────────────────────────────────
// POST takes a JSON body matching StockPriceHistory (with optional
// trigger_yfinance flag). The granular FE-005 ticket assumed multipart file
// upload; the actual spec is JSON. Tracked in phase summary.

export function getStockPrices(vestingMonth: string): Promise<StockPriceEntry[]> {
  return request.get(`/monthly-report/stock-prices/${vestingMonth}`)
}

export function uploadStockPrices(
  data: StockPriceHistory & { trigger_yfinance?: boolean },
): Promise<StockPriceHistory> {
  return request.post('/monthly-report/stock-prices', data)
}

// ─── Insurance surrender values (解約金) ──────────────────────────────────────

export function getInsuranceValues(vestingMonth: string): Promise<InsuranceValueMonth[]> {
  return request.get(`/monthly-report/insurance-values/${vestingMonth}`)
}

export function upsertInsuranceValue(
  data: InsuranceValueCreate,
): Promise<InsuranceValueCreate> {
  return request.post('/monthly-report/insurance-values', data)
}

// ─── Estate market values (估值) ──────────────────────────────────────────────

export function getEstateValues(vestingMonth: string): Promise<EstateValueMonth[]> {
  return request.get(`/monthly-report/estate-values/${vestingMonth}`)
}

export function upsertEstateValue(data: EstateValueCreate): Promise<EstateValueCreate> {
  return request.post('/monthly-report/estate-values', data)
}

export function getEstateValueSuggestions(
  vestingMonth: string,
): Promise<EstateValueSuggestion[]> {
  return request.get(`/monthly-report/estate-values/${vestingMonth}/suggestions`)
}

export function refreshHousePriceIndex(): Promise<IndexRefreshResult> {
  return request.post('/monthly-report/estate-values/refresh-index')
}
