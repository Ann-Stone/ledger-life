// 資料匯入 (Data import) page.
export default {
  title: 'Data Import',
  subtitle: 'Batch import stock prices, FX rates and invoices',

  // Stock price import card.
  stockTitle: 'Stock Price Import',
  stockDesc:
    'Fetch daily prices for every ticker in your stock transactions over the given period via yfinance and write them into Stock_Price_History.',
  stockHint:
    'Leave blank for today; enter YYYYMM to fetch the last trading day of that month.',
  stockButton: 'Import Prices',
  stockScheduled: 'Stock price import scheduled',
  stockFailed: 'Stock price import failed',

  // FX rate import card.
  fxTitle: 'FX Rate Import',
  fxDesc:
    'Fetch foreign-currency buy rates for the given period from SinoPac Bank and upsert them into FX_Rate.',
  fxHint:
    'Leave blank for today; enter YYYYMM to fetch the last day of that month.',
  fxButton: 'Import Rates',
  fxScheduled: 'FX rate import scheduled',
  fxFailed: 'FX rate import failed',

  // Invoice import card.
  invoiceTitle: 'Invoice Import',
  invoiceDesc:
    'Upload the CSV (pipe-separated) exported from the MOF e-invoice platform; the system parses and de-duplicates it, writes into Journal and reports the import result.',
  periodPlaceholder: 'Blank for today',
  chooseCsv: 'Choose CSV',
  invoiceButton: 'Import Invoices',
  invoiceFailed: 'Invoice import failed',
  pickCsvFirst: 'Please choose a CSV file to import first',
  invoiceEmptyHint:
    'CSV only; pick a file then press "Import Invoices".',
  // n/skip/fail are integer counts.
  lastResult:
    'Last run: {imported} imported · {skipped} skipped · {failed} failed',
  resultSummary: '{imported} imported, {skipped} skipped, {failed} failed',
  monthImported: '{month}: {imported} imported',
  monthSkipped: ' · {skipped} skipped',
}
