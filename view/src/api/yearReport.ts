import request from '@/utils/request'
import type {
  AssetReport,
  BalanceReport,
  BudgetVariance,
  CashFlow,
  ExpenditureComposition,
  ExpenditureReport,
  ExpenseInsights,
  IncomeExpenseReport,
  IncomeStatementReport,
  StockAllocationReport,
} from '@/types/models'

export function getBalanceReport(): Promise<BalanceReport> {
  return request.get('/reports/balance')
}

export function getExpenditureReport(
  type: string,
  params: { vesting_month: string },
): Promise<ExpenditureReport> {
  return request.get(`/reports/expenditure/${type}`, { params })
}

export function getIncomeExpenseReport(
  type: string,
  params: { vesting_month: string },
): Promise<IncomeExpenseReport> {
  return request.get(`/reports/income-expense/${type}`, { params })
}

export function getIncomeStatement(
  type: string,
  params: { vesting_month: string },
): Promise<IncomeStatementReport> {
  return request.get(`/reports/income-statement/${type}`, { params })
}

export function getExpenditureComposition(
  type: string,
  params: { vesting_month: string },
): Promise<ExpenditureComposition> {
  return request.get(`/reports/expenditure-composition/${type}`, { params })
}

export function getBudgetVariance(year: string | number): Promise<BudgetVariance> {
  return request.get(`/reports/budget-variance/${year}`)
}

export function getCashFlow(
  type: string,
  params: { vesting_month: string },
): Promise<CashFlow> {
  return request.get(`/reports/cash-flow/${type}`, { params })
}

export function getExpenseInsights(year: string | number): Promise<ExpenseInsights> {
  return request.get(`/reports/expense-insights/${year}`)
}

export function getAssetsReport(): Promise<AssetReport> {
  return request.get('/reports/assets')
}

export function getStockAllocation(): Promise<StockAllocationReport> {
  return request.get('/reports/stock-allocation')
}
