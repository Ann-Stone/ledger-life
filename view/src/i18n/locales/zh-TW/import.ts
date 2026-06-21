// 資料匯入 (Data import) page.
export default {
  title: '資料匯入',
  subtitle: '批次匯入股價、匯率與發票',

  // Stock price import card.
  stockTitle: '股價匯入',
  stockDesc:
    '透過 yfinance 抓取股票交易紀錄中所有 ticker 的指定期間日線價格，寫入 Stock_Price_History。',
  stockHint: '留白表示今日；填入 YYYYMM 抓該月最後一個交易日的價格。',
  stockButton: '匯入股價',
  stockScheduled: '股價匯入已排程',
  stockFailed: '股價匯入失敗',

  // FX rate import card.
  fxTitle: '匯率匯入',
  fxDesc: '從永豐銀行抓取指定期間的外幣買入匯率，upsert 至 FX_Rate。',
  fxHint: '留白表示今日；填入 YYYYMM 抓該月最後一日的匯率。',
  fxButton: '匯入匯率',
  fxScheduled: '匯率匯入已排程',
  fxFailed: '匯率匯入失敗',

  // Invoice import card.
  invoiceTitle: '發票匯入',
  invoiceDesc:
    '上傳財政部電子發票平台匯出的 CSV（pipe 分隔），系統會解析、去重後寫入 Journal，並回報匯入結果。',
  periodPlaceholder: '留白表示今日',
  chooseCsv: '選擇 CSV 檔',
  invoiceButton: '匯入發票',
  invoiceFailed: '發票匯入失敗',
  pickCsvFirst: '請先選擇要匯入的 CSV 檔',
  invoiceEmptyHint: '僅接受 CSV 檔；選擇檔案後按「匯入發票」即可。',
  // n/skip/fail are integer counts.
  lastResult: '最近一次：匯入 {imported} 筆 · 略過 {skipped} 筆 · 失敗 {failed} 筆',
  resultSummary: '匯入 {imported} 筆，略過 {skipped} 筆，失敗 {failed} 筆',
  monthImported: '{month}：匯入 {imported} 筆',
  monthSkipped: ' · 略過 {skipped} 筆',
}
