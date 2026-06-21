import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useFetchState } from '@/composables/useFetchState'
import {
  getAssetsReport,
  getBalanceReport,
  getBudgetVariance,
  getCashFlow,
  getExpenditureComposition,
  getExpenditureReport,
  getExpenseInsights,
  getIncomeExpenseReport,
  getIncomeStatement,
  getStockAllocation,
} from '@/api/yearReport'

export const useYearReportStore = defineStore('yearReport', () => {
  const selectedYear = ref<number>(new Date().getFullYear())

  // Sync the year selection, then return the anchor year for the request.
  function anchorYear(year?: number): number {
    if (year != null) selectedYear.value = year
    return year ?? selectedYear.value
  }

  // API anchor is vesting_month YYYYMM; annual reports anchor on December
  // of selectedYear when only a year is supplied.
  function anchorMonth(year?: number): string {
    return `${anchorYear(year)}12`
  }

  // Balance report — API takes no year param; year is selection state only.
  const balance = useFetchState((year?: number) => {
    anchorYear(year)
    return getBalanceReport()
  })

  const expenditure = useFetchState((type: string, year?: number) =>
    getExpenditureReport(type, { vesting_month: anchorMonth(year) }),
  )

  const incomeExpense = useFetchState((type: string, year?: number) =>
    getIncomeExpenseReport(type, { vesting_month: anchorMonth(year) }),
  )

  // Comprehensive income statement (本業/投資/綜合損益).
  const incomeStatement = useFetchState((type: string, year?: number) =>
    getIncomeStatement(type, { vesting_month: anchorMonth(year) }),
  )

  const composition = useFetchState((type: string, year?: number) =>
    getExpenditureComposition(type, { vesting_month: anchorMonth(year) }),
  )

  // Budget vs actual variance — annual, keyed by year only.
  const budget = useFetchState((year?: number) => getBudgetVariance(anchorYear(year)))

  // Cash-flow statement (生活/投資/債務).
  const cashFlow = useFetchState((type: string, year?: number) =>
    getCashFlow(type, { vesting_month: anchorMonth(year) }),
  )

  // Expense insights — YoY + largest transactions, keyed by year.
  const insights = useFetchState((year?: number) => getExpenseInsights(anchorYear(year)))

  // Assets report — API takes no year param.
  const assets = useFetchState((year?: number) => {
    anchorYear(year)
    return getAssetsReport()
  })

  const stockAllocationState = useFetchState(() => getStockAllocation())

  return {
    selectedYear,
    balanceReport: balance.data,
    balanceLoading: balance.loading,
    fetchBalanceReport: balance.fetch,
    expenditureReport: expenditure.data,
    expenditureLoading: expenditure.loading,
    fetchExpenditureReport: expenditure.fetch,
    incomeExpenseReport: incomeExpense.data,
    incomeExpenseLoading: incomeExpense.loading,
    fetchIncomeExpenseReport: incomeExpense.fetch,
    incomeStatementReport: incomeStatement.data,
    incomeStatementLoading: incomeStatement.loading,
    fetchIncomeStatement: incomeStatement.fetch,
    compositionReport: composition.data,
    compositionLoading: composition.loading,
    fetchExpenditureComposition: composition.fetch,
    budgetReport: budget.data,
    budgetLoading: budget.loading,
    fetchBudgetVariance: budget.fetch,
    cashFlowReport: cashFlow.data,
    cashFlowLoading: cashFlow.loading,
    fetchCashFlow: cashFlow.fetch,
    insightsReport: insights.data,
    insightsLoading: insights.loading,
    fetchExpenseInsights: insights.fetch,
    assetsReport: assets.data,
    assetsLoading: assets.loading,
    fetchAssetsReport: assets.fetch,
    stockAllocation: stockAllocationState.data,
    stockAllocationLoading: stockAllocationState.loading,
    fetchStockAllocation: stockAllocationState.fetch,
  }
})
