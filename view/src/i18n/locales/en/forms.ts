// Shared detail-form field components (Stock / Estate / Insurance DetailFormFields).
export default {
  holdingId: 'Holding ID',
  estateId: 'Estate ID',
  insuranceId: 'Insurance ID',
  quantity: 'Quantity',
  unitPrice: 'Amount',
  accountId: 'Account ID',
  accountName: 'Account Name',
  accountIdPlaceholder: 'e.g. BANK-CHASE-01',
  accountNamePlaceholder: 'e.g. Chase Checking',
  cashDividendHint: 'Cash dividend quantity can stay 0; the amount is auto-filled from the main form amount (incl. sign).',
  amountAutoHint: 'Amount is auto-filled from the main form amount (incl. sign).',
  // Loan repayment split (principal + interest, both positive magnitudes)
  loanPrincipal: 'Principal',
  loanInterest: 'Interest',
  loanSplitHint: 'principal + interest = {total}; the main amount auto-fills to −(principal+interest)',
  // Stock execution types
  stockBuy: 'Buy',
  stockSell: 'Sell',
  stockStockDividend: 'Stock dividend',
  stockCashDividend: 'Cash dividend',
  // Estate execution types
  estateTax: 'Tax',
  estateFee: 'Management fee',
  estateInsurance: 'Insurance',
  estateFix: 'Maintenance',
  estateRent: 'Rent',
  estateDeposit: 'Deposit',
  // Insurance execution types
  insurancePay: 'Payment',
  insuranceCash: 'Cash back',
  insuranceReturn: 'Refund',
  insuranceExpect: 'Expected',
}
