// Shared detail-form field components (Stock / Estate / Insurance DetailFormFields).
export default {
  holdingId: '持有 ID',
  estateId: '房產 ID',
  insuranceId: '保險 ID',
  quantity: '數量',
  unitPrice: '金額',
  accountId: '帳戶 ID',
  accountName: '帳戶名稱',
  accountIdPlaceholder: '例如 BANK-CHASE-01',
  accountNamePlaceholder: '例如 Chase Checking',
  cashDividendHint: '現金股息數量可留 0；金額會自動帶入主表單的金額（含正負號）',
  amountAutoHint: '金額會自動帶入主表單的金額（含正負號）',
  // Loan repayment split (本金 + 利息, both positive magnitudes)
  loanPrincipal: '本金',
  loanInterest: '利息',
  loanSplitHint: '本金 + 利息 = {total}；主表單金額自動帶入 −(本金+利息)',
  // Stock execution types
  stockBuy: '買入 (buy)',
  stockSell: '賣出 (sell)',
  stockStockDividend: '股票股利 (stock)',
  stockCashDividend: '現金股利 (cash)',
  // Estate execution types
  estateTax: '稅務 (tax)',
  estateFee: '管理費 (fee)',
  estateInsurance: '保險 (insurance)',
  estateFix: '維修 (fix)',
  estateRent: '租金 (rent)',
  estateDeposit: '押金 (deposit)',
  // Insurance execution types
  insurancePay: '繳費 (pay)',
  insuranceCash: '現金回饋 (cash)',
  insuranceReturn: '退費 (return)',
  insuranceExpect: '預期 (expect)',
}
