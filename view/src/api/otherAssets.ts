import request from '@/utils/request'
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

export function getStocks(params: { asset_id: string }): Promise<StockAsset[]> {
  return request.get('/assets/stocks', { params })
}

export function getStockPnlSummary(assetId: string): Promise<StockPnlSummary[]> {
  return request.get('/assets/stocks/summary', { params: { asset_id: assetId } })
}

export function createStock(data: StockAssetCreate): Promise<StockAsset> {
  return request.post('/assets/stocks', data)
}

export function updateStock(id: string, data: StockAssetUpdate): Promise<StockAsset> {
  return request.put(`/assets/stocks/${id}`, data)
}

export function deleteStock(id: string): Promise<null> {
  return request.delete(`/assets/stocks/${id}`)
}

export function getStockDetails(stockId: string): Promise<StockJournal[]> {
  return request.get(`/assets/stocks/${stockId}/details`)
}

export function createStockDetail(
  stockId: string,
  data: StockJournalCreate,
): Promise<StockJournal> {
  return request.post(`/assets/stocks/${stockId}/details`, data)
}

export function updateStockDetail(
  distinctNumber: number,
  data: StockJournalUpdate,
): Promise<StockJournal> {
  return request.put(`/assets/stocks/details/${distinctNumber}`, data)
}

export function deleteStockDetail(distinctNumber: number): Promise<null> {
  return request.delete(`/assets/stocks/details/${distinctNumber}`)
}

// ─── Estates ─────────────────────────────────────────────────────────────────

export function getEstates(params: { asset_id: string }): Promise<EstateAsset[]> {
  return request.get('/assets/estates', { params })
}

export function createEstate(data: EstateAssetCreate): Promise<EstateAsset> {
  return request.post('/assets/estates', data)
}

export function updateEstate(id: string, data: EstateAssetUpdate): Promise<EstateAsset> {
  return request.put(`/assets/estates/${id}`, data)
}

export function deleteEstate(id: string): Promise<null> {
  return request.delete(`/assets/estates/${id}`)
}

export function getEstateDetails(estateId: string): Promise<EstateJournal[]> {
  return request.get(`/assets/estates/${estateId}/details`)
}

export function createEstateDetail(
  estateId: string,
  data: EstateJournalCreate,
): Promise<EstateJournal> {
  return request.post(`/assets/estates/${estateId}/details`, data)
}

export function updateEstateDetail(
  distinctNumber: number,
  data: EstateJournalUpdate,
): Promise<EstateJournal> {
  return request.put(`/assets/estates/details/${distinctNumber}`, data)
}

export function deleteEstateDetail(distinctNumber: number): Promise<null> {
  return request.delete(`/assets/estates/details/${distinctNumber}`)
}

// ─── Insurances ──────────────────────────────────────────────────────────────

export function getInsurances(params: { asset_id: string }): Promise<InsuranceAsset[]> {
  return request.get('/assets/insurances', { params })
}

export function createInsurance(data: InsuranceAssetCreate): Promise<InsuranceAsset> {
  return request.post('/assets/insurances', data)
}

export function updateInsurance(
  id: string,
  data: InsuranceAssetUpdate,
): Promise<InsuranceAsset> {
  return request.put(`/assets/insurances/${id}`, data)
}

export function deleteInsurance(id: string): Promise<null> {
  return request.delete(`/assets/insurances/${id}`)
}

export function getInsuranceDetails(insuranceId: string): Promise<InsuranceJournal[]> {
  return request.get(`/assets/insurances/${insuranceId}/details`)
}

export function createInsuranceDetail(
  insuranceId: string,
  data: InsuranceJournalCreate,
): Promise<InsuranceJournal> {
  return request.post(`/assets/insurances/${insuranceId}/details`, data)
}

export function updateInsuranceDetail(
  distinctNumber: number,
  data: InsuranceJournalUpdate,
): Promise<InsuranceJournal> {
  return request.put(`/assets/insurances/details/${distinctNumber}`, data)
}

export function deleteInsuranceDetail(distinctNumber: number): Promise<null> {
  return request.delete(`/assets/insurances/details/${distinctNumber}`)
}

// ─── Loans ───────────────────────────────────────────────────────────────────

export function getLoans(): Promise<LoanAsset[]> {
  return request.get('/assets/loans')
}

export function getLoan(id: string): Promise<LoanAsset> {
  return request.get(`/assets/loans/${id}`)
}

export function createLoan(data: LoanAssetCreate): Promise<LoanAsset> {
  return request.post('/assets/loans', data)
}

export function updateLoan(id: string, data: LoanAssetUpdate): Promise<LoanAsset> {
  return request.put(`/assets/loans/${id}`, data)
}

export function deleteLoan(id: string): Promise<null> {
  return request.delete(`/assets/loans/${id}`)
}

export function getLoanDetails(loanId: string): Promise<LoanJournal[]> {
  return request.get(`/assets/loans/${loanId}/details`)
}

export function createLoanDetail(
  loanId: string,
  data: LoanJournalCreate,
): Promise<LoanJournal> {
  return request.post(`/assets/loans/${loanId}/details`, data)
}

export function updateLoanDetail(
  distinctNumber: number,
  data: LoanJournalUpdate,
): Promise<LoanJournal> {
  return request.put(`/assets/loans/details/${distinctNumber}`, data)
}

export function deleteLoanDetail(distinctNumber: number): Promise<null> {
  return request.delete(`/assets/loans/details/${distinctNumber}`)
}

export function getLoanSelection(): Promise<LoanSelection[]> {
  return request.get('/assets/loans/selection')
}

// ─── Other assets ────────────────────────────────────────────────────────────

export function getOtherAssets(): Promise<OtherAsset[]> {
  return request.get('/assets/other-assets')
}

export function getOtherAssetItems(): Promise<OtherAssetItem[]> {
  return request.get('/assets/other-assets/items')
}

export function createOtherAsset(data: OtherAssetCreate): Promise<OtherAsset> {
  return request.post('/assets/other-assets', data)
}

export function updateOtherAsset(id: string, data: OtherAssetUpdate): Promise<OtherAsset> {
  return request.put(`/assets/other-assets/${id}`, data)
}

export function deleteOtherAsset(id: string): Promise<null> {
  return request.delete(`/assets/other-assets/${id}`)
}
