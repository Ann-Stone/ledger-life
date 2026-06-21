import { defineStore } from 'pinia'
import { ref } from 'vue'
import dayjs from 'dayjs'
import { useFetchState } from '@/composables/useFetchState'
import {
  getEstateValues,
  getEstateValueSuggestions,
  getExpenditureBudget,
  getExpenditureRatio,
  getInvestRatio,
  getInsuranceValues,
  getJournals,
  getLiability,
  getStockPrices,
  refreshHousePriceIndex,
} from '@/api/cashFlow'
import type {
  EstateValueMonth,
  EstateValueSuggestion,
  IndexRefreshResult,
  InsuranceValueMonth,
  Journal,
  StockPriceRead,
} from '@/types/models'

export const useCashFlowStore = defineStore('cashFlow', () => {
  const selectedMonth = ref<string>(dayjs().format('YYYYMM'))

  function anchorMonth(month?: string): string {
    return month ?? selectedMonth.value
  }

  // Journals — the response also carries the month's realized gain/loss.
  const journalsGainLoss = ref<number>(0)
  const journalsState = useFetchState(async (month?: string) => {
    const res = await getJournals(anchorMonth(month))
    journalsGainLoss.value = res.gain_loss
    return res.items
  }, [] as Journal[])

  const expenditureBudget = useFetchState((month?: string) =>
    getExpenditureBudget(anchorMonth(month)),
  )

  const expenditureRatio = useFetchState((month?: string) =>
    getExpenditureRatio(anchorMonth(month)),
  )

  const investRatio = useFetchState((month?: string) => getInvestRatio(anchorMonth(month)))

  const liability = useFetchState((month?: string) => getLiability(anchorMonth(month)))

  const stockPrices = useFetchState(
    (month?: string) => getStockPrices(anchorMonth(month)),
    [] as StockPriceRead[],
  )

  // Insurance surrender values (解約金)
  const insuranceValues = useFetchState(
    (month?: string) => getInsuranceValues(anchorMonth(month)),
    [] as InsuranceValueMonth[],
  )

  // Estate market values (估值)
  const estateValues = useFetchState(
    (month?: string) => getEstateValues(anchorMonth(month)),
    [] as EstateValueMonth[],
  )

  // Index-based suggested market values (P3) — no loading flag by design.
  const estateSuggestions = ref<EstateValueSuggestion[]>([])
  async function fetchEstateSuggestions(month?: string) {
    estateSuggestions.value = await getEstateValueSuggestions(anchorMonth(month))
  }
  async function refreshEstateIndex(): Promise<IndexRefreshResult> {
    const res = await refreshHousePriceIndex()
    await fetchEstateSuggestions()
    return res
  }

  return {
    selectedMonth,
    journals: journalsState.data,
    journalsLoading: journalsState.loading,
    journalsGainLoss,
    fetchJournals: journalsState.fetch,
    expenditureBudget: expenditureBudget.data,
    expenditureBudgetLoading: expenditureBudget.loading,
    fetchExpenditureBudget: expenditureBudget.fetch,
    expenditureRatio: expenditureRatio.data,
    expenditureRatioLoading: expenditureRatio.loading,
    fetchExpenditureRatio: expenditureRatio.fetch,
    investRatio: investRatio.data,
    investRatioLoading: investRatio.loading,
    fetchInvestRatio: investRatio.fetch,
    liability: liability.data,
    liabilityLoading: liability.loading,
    fetchLiability: liability.fetch,
    stockPrices: stockPrices.data,
    stockPricesLoading: stockPrices.loading,
    fetchStockPrices: stockPrices.fetch,
    insuranceValues: insuranceValues.data,
    insuranceValuesLoading: insuranceValues.loading,
    fetchInsuranceValues: insuranceValues.fetch,
    estateValues: estateValues.data,
    estateValuesLoading: estateValues.loading,
    fetchEstateValues: estateValues.fetch,
    estateSuggestions,
    fetchEstateSuggestions,
    refreshEstateIndex,
  }
})
