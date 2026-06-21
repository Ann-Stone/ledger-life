import request from '@/utils/request'
import type {
  Account,
  AccountCreate,
  AccountUpdate,
  Alarm,
  AlarmCreate,
  AlarmUpdate,
  Budget,
  BudgetRead,
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

export function getAccounts(params?: {
  name?: string
  account_type?: string
  in_use?: string
}): Promise<Account[]> {
  return request.get('/settings/accounts', { params })
}

export function createAccount(data: AccountCreate): Promise<Account> {
  return request.post('/settings/accounts', data)
}

export function updateAccount(id: number, data: AccountUpdate): Promise<Account> {
  return request.put(`/settings/accounts/${id}`, data)
}

export function deleteAccount(id: number): Promise<null> {
  return request.delete(`/settings/accounts/${id}`)
}

// ─── Alarms ──────────────────────────────────────────────────────────────────

export function getAlarms(): Promise<Alarm[]> {
  return request.get('/settings/alarms')
}

export function createAlarm(data: AlarmCreate): Promise<Alarm> {
  return request.post('/settings/alarms', data)
}

export function updateAlarm(id: number, data: AlarmUpdate): Promise<Alarm> {
  return request.put(`/settings/alarms/${id}`, data)
}

export function deleteAlarm(id: number): Promise<null> {
  return request.delete(`/settings/alarms/${id}`)
}

// ─── Budgets ─────────────────────────────────────────────────────────────────

export function getBudgetYears(): Promise<string[]> {
  return request.get('/settings/budgets/year-range')
}

export function getBudgets(year: number): Promise<BudgetRead[]> {
  return request.get(`/settings/budgets/${year}`)
}

export function updateBudgets(data: Budget[]): Promise<Budget[]> {
  return request.put('/settings/budgets', data)
}

/** Compute a suggested budget for `year` from recent years; does NOT persist. */
export function suggestBudget(year: number): Promise<BudgetRead[]> {
  return request.post(`/settings/budgets/${year}/suggest`)
}

/** Upsert (insert-or-update) the provided budget rows for `year`. */
export function applyBudget(year: number, data: Budget[]): Promise<BudgetRead[]> {
  return request.post(`/settings/budgets/${year}/apply`, data)
}

// ─── Codes ───────────────────────────────────────────────────────────────────

export function getCodes(): Promise<CodeData[]> {
  return request.get('/settings/codes')
}

export function getCodesWithSub(): Promise<CodeDataWithSub[]> {
  return request.get('/settings/codes/all-with-sub')
}

export function createCode(data: CodeDataCreate): Promise<CodeData> {
  return request.post('/settings/codes', data)
}

export function updateCode(id: string, data: CodeDataUpdate): Promise<CodeData> {
  return request.put(`/settings/codes/${id}`, data)
}

export function deleteCode(id: string): Promise<null> {
  return request.delete(`/settings/codes/${id}`)
}

// ─── Sub-codes ───────────────────────────────────────────────────────────────

export function createSubCode(data: CodeDataCreate): Promise<CodeData> {
  return request.post('/settings/sub-codes', data)
}

export function updateSubCode(id: string, data: CodeDataUpdate): Promise<CodeData> {
  return request.put(`/settings/sub-codes/${id}`, data)
}

export function deleteSubCode(id: string): Promise<null> {
  return request.delete(`/settings/sub-codes/${id}`)
}

// ─── Credit cards ────────────────────────────────────────────────────────────

export function getCreditCards(params?: {
  card_name?: string
  in_use?: string
}): Promise<CreditCard[]> {
  return request.get('/settings/credit-cards', { params })
}

export function createCreditCard(data: CreditCardCreate): Promise<CreditCard> {
  return request.post('/settings/credit-cards', data)
}

export function updateCreditCard(id: string, data: CreditCardUpdate): Promise<CreditCard> {
  return request.put(`/settings/credit-cards/${id}`, data)
}

export function deleteCreditCard(id: string): Promise<null> {
  return request.delete(`/settings/credit-cards/${id}`)
}

// ─── Stock categories ────────────────────────────────────────────────────────

export function getStockCategories(): Promise<StockCategory[]> {
  return request.get('/settings/stock-categories')
}

export function createStockCategory(data: StockCategoryCreate): Promise<StockCategory> {
  return request.post('/settings/stock-categories', data)
}

export function updateStockCategory(
  id: string,
  data: StockCategoryUpdate,
): Promise<StockCategory> {
  return request.put(`/settings/stock-categories/${id}`, data)
}

export function deleteStockCategory(id: string): Promise<null> {
  return request.delete(`/settings/stock-categories/${id}`)
}
