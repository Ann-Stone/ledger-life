import { defineStore } from 'pinia'
import { ref } from 'vue'
import { useFetchState } from '@/composables/useFetchState'
import {
  getEstateDetails,
  getEstates,
  getInsuranceDetails,
  getInsurances,
  getLoanDetails,
  getLoans,
  getOtherAssets,
  getStockDetails,
  getStockPnlSummary,
  getStocks,
} from '@/api/otherAssets'
import type {
  EstateAsset,
  EstateJournal,
  InsuranceAsset,
  InsuranceJournal,
  LoanAsset,
  LoanJournal,
  OtherAsset,
  StockAsset,
  StockJournal,
  StockPnlSummary,
} from '@/types/models'

export const useOtherAssetsStore = defineStore('otherAssets', () => {
  const activeTab = ref<string>('stocks')

  // Stocks
  const stocks = useFetchState(
    (assetId: string) => getStocks({ asset_id: assetId }),
    [] as StockAsset[],
  )
  const stockDetails = useFetchState(
    (stockId: string) => getStockDetails(stockId),
    [] as StockJournal[],
  )
  // Per-holding computed P&L (cost / market value / realized / unrealized /
  // yields) for the current asset category's stock table.
  const stockPnl = useFetchState(
    (assetId: string) => getStockPnlSummary(assetId),
    [] as StockPnlSummary[],
  )

  // Estates
  const estates = useFetchState(
    (assetId: string) => getEstates({ asset_id: assetId }),
    [] as EstateAsset[],
  )
  const estateDetails = useFetchState(
    (estateId: string) => getEstateDetails(estateId),
    [] as EstateJournal[],
  )

  // Insurances
  const insurances = useFetchState(
    (assetId: string) => getInsurances({ asset_id: assetId }),
    [] as InsuranceAsset[],
  )
  const insuranceDetails = useFetchState(
    (insuranceId: string) => getInsuranceDetails(insuranceId),
    [] as InsuranceJournal[],
  )

  // Loans
  const loans = useFetchState(() => getLoans(), [] as LoanAsset[])
  const loanDetails = useFetchState(
    (loanId: string) => getLoanDetails(loanId),
    [] as LoanJournal[],
  )

  // Other assets
  const otherAssets = useFetchState(() => getOtherAssets(), [] as OtherAsset[])

  return {
    activeTab,
    stocks: stocks.data,
    stocksLoading: stocks.loading,
    fetchStocks: stocks.fetch,
    stockDetails: stockDetails.data,
    stockDetailsLoading: stockDetails.loading,
    fetchStockDetails: stockDetails.fetch,
    stockPnl: stockPnl.data,
    stockPnlLoading: stockPnl.loading,
    fetchStockPnl: stockPnl.fetch,
    estates: estates.data,
    estatesLoading: estates.loading,
    fetchEstates: estates.fetch,
    estateDetails: estateDetails.data,
    estateDetailsLoading: estateDetails.loading,
    fetchEstateDetails: estateDetails.fetch,
    insurances: insurances.data,
    insurancesLoading: insurances.loading,
    fetchInsurances: insurances.fetch,
    insuranceDetails: insuranceDetails.data,
    insuranceDetailsLoading: insuranceDetails.loading,
    fetchInsuranceDetails: insuranceDetails.fetch,
    loans: loans.data,
    loansLoading: loans.loading,
    fetchLoans: loans.fetch,
    loanDetails: loanDetails.data,
    loanDetailsLoading: loanDetails.loading,
    fetchLoanDetails: loanDetails.fetch,
    otherAssets: otherAssets.data,
    otherAssetsLoading: otherAssets.loading,
    fetchOtherAssets: otherAssets.fetch,
  }
})
