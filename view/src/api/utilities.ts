import request from '@/utils/request'
import type {
  ImportResult,
  InvoiceImportResult,
  SelectionAccount,
  SelectionCode,
  SelectionCreditCard,
  SelectionEstate,
  SelectionInsurance,
  SelectionLoan,
  SelectionOtherAssetType,
  SelectionStock,
} from '@/types/models'

// ─── Selection dropdowns ─────────────────────────────────────────────────────

export function getAccountSelections(): Promise<SelectionAccount[]> {
  return request.get('/utilities/selections/accounts')
}

export function getCodeSelections(codeGroup?: string): Promise<SelectionCode[]> {
  const url = codeGroup
    ? `/utilities/selections/codes/${codeGroup}`
    : '/utilities/selections/codes'
  return request.get(url)
}

export function getCreditCardSelections(): Promise<SelectionCreditCard[]> {
  return request.get('/utilities/selections/credit-cards')
}

export function getEstateSelections(): Promise<SelectionEstate[]> {
  return request.get('/utilities/selections/estates')
}

export function getInsuranceSelections(): Promise<SelectionInsurance[]> {
  return request.get('/utilities/selections/insurances')
}

export function getLoanSelections(): Promise<SelectionLoan[]> {
  return request.get('/utilities/selections/loans')
}

export function getOtherAssetTypeSelections(): Promise<SelectionOtherAssetType[]> {
  return request.get('/utilities/selections/other-asset-types')
}

export function getStockSelections(): Promise<SelectionStock[]> {
  return request.get('/utilities/selections/stocks')
}

// ─── Import endpoints ────────────────────────────────────────────────────────
// Stock/FX kick off background tasks via a JSON body { period: "YYYYMM" }
// (empty string falls back to today). Invoices are uploaded directly as a
// multipart CSV and processed synchronously, returning the import counts.

export function importStockPrices(period: string): Promise<ImportResult> {
  return request.post('/utilities/import/stock-prices', { period })
}

export function importFxRates(period: string): Promise<ImportResult> {
  return request.post('/utilities/import/fx-rates', { period })
}

export function importInvoices(file: File): Promise<InvoiceImportResult> {
  const form = new FormData()
  form.append('file', file)
  // axios sets the multipart boundary header automatically for FormData.
  return request.post('/utilities/import/invoices', form)
}
