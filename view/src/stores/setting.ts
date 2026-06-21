import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useFetchState } from '@/composables/useFetchState'
import {
  getAccounts,
  getAlarms,
  getBudgetYears,
  getBudgets,
  getCodesWithSub,
  getCreditCards,
  getStockCategories,
} from '@/api/setting'
import type {
  Account,
  Alarm,
  BudgetRead,
  CodeDataWithSub,
  CreditCard,
  StockCategory,
} from '@/types/models'

export const useSettingStore = defineStore('setting', () => {
  // Accounts
  const accounts = useFetchState(
    (params?: { name?: string; account_type?: string; in_use?: string }) =>
      getAccounts(params),
    [] as Account[],
  )

  // Alarms
  const alarms = useFetchState(() => getAlarms(), [] as Alarm[])

  // Budgets
  const budgets = useFetchState((year: number) => getBudgets(year), [] as BudgetRead[])
  const budgetYears = ref<string[]>([])
  async function fetchBudgetYears() {
    budgetYears.value = await getBudgetYears()
  }

  // Codes (with sub)
  const codes = useFetchState(() => getCodesWithSub(), [] as CodeDataWithSub[])

  // Credit cards
  const creditCards = useFetchState(
    (params?: { card_name?: string; in_use?: string }) => getCreditCards(params),
    [] as CreditCard[],
  )

  // Stock categories (allocation dictionary)
  const stockCategories = useFetchState(() => getStockCategories(), [] as StockCategory[])

  return {
    accounts: accounts.data,
    accountsLoading: accounts.loading,
    fetchAccounts: accounts.fetch,
    alarms: alarms.data,
    alarmsLoading: alarms.loading,
    fetchAlarms: alarms.fetch,
    budgets: budgets.data,
    budgetsLoading: budgets.loading,
    budgetYears,
    fetchBudgets: budgets.fetch,
    fetchBudgetYears,
    codesWithSub: codes.data,
    codesLoading: codes.loading,
    fetchCodesWithSub: codes.fetch,
    creditCards: creditCards.data,
    creditCardsLoading: creditCards.loading,
    fetchCreditCards: creditCards.fetch,
    stockCategories: stockCategories.data,
    stockCategoriesLoading: stockCategories.loading,
    fetchStockCategories: stockCategories.fetch,
  }
})
