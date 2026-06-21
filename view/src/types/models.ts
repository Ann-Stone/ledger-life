// =============================================================================
// Networth API — TypeScript model definitions
// Single source of truth. All field names are snake_case to match the API.
// Y/N flag fields are typed as `string`, not `boolean`.
// =============================================================================

// ─── Shared envelope & selection ─────────────────────────────────────────────

export interface ApiResponse<T> {
  status: number
  data: T
  msg: string
}

/**
 * Grouped option list returned by every /utilities/selections/* endpoint.
 * Each group has a label (e.g. account_type) and an `options` array of
 * `{label, value}` pairs ready to feed an `<el-select>`.
 */
export interface SelectionOption {
  label: string
  value: string
}

export interface SelectionGroup {
  label: string
  options: SelectionOption[]
}

export type SelectionItem = SelectionOption

// ─── Settings — Account ──────────────────────────────────────────────────────

export interface Account {
  id: number
  account_id: string
  name: string
  account_type: string
  fx_code: string
  is_calculate: string  // Y/N
  in_use: string        // Y/N
  discount: number
  memo?: string | null
  owner?: string | null
  account_index: number
}

export interface AccountCreate {
  account_id: string
  name: string
  account_type: string
  fx_code: string
  is_calculate?: string
  in_use?: string
  discount?: number
  memo?: string | null
  owner?: string | null
  account_index?: number
}

export type AccountUpdate = Partial<AccountCreate>

// ─── Settings — Alarm ────────────────────────────────────────────────────────

export type AlarmType = 'Y' | 'M'

export interface Alarm {
  alarm_id: number
  alarm_type: AlarmType
  // MMDD when alarm_type === 'Y', DD when alarm_type === 'M'
  alarm_date: string
  content: string
  due_date?: string | null
}

export interface AlarmCreate {
  alarm_type: AlarmType
  alarm_date: string
  content: string
  due_date?: string | null
}

export type AlarmUpdate = Partial<AlarmCreate>

// ─── Settings — Budget ───────────────────────────────────────────────────────

export interface Budget {
  budget_year: string   // YYYY
  category_code: string
  category_name: string
  code_type: string
  expected01: number
  expected02: number
  expected03: number
  expected04: number
  expected05: number
  expected06: number
  expected07: number
  expected08: number
  expected09: number
  expected10: number
  expected11: number
  expected12: number
  annual_amount?: number | null   // envelope for annual-event categories
}

export type BudgetRead = Budget

// ─── Settings — CodeData (codes + sub-codes share schema) ────────────────────

export interface CodeData {
  code_id: string
  code_type: string
  name: string
  parent_id?: string | null
  in_use: string        // Y/N
  code_index: number
  is_annual_event: boolean   // budget as a single annual envelope
}

export interface CodeDataWithSub extends CodeData {
  sub_codes?: CodeData[]
}

export interface CodeDataCreate {
  code_id: string
  code_type: string
  name: string
  parent_id?: string | null
  in_use?: string
  code_index?: number
  is_annual_event?: boolean
}

export type CodeDataUpdate = Partial<CodeDataCreate>

// ─── Settings — CreditCard ───────────────────────────────────────────────────

export interface CreditCard {
  credit_card_id: string
  card_name: string
  card_no?: string | null
  last_day?: number | null
  charge_day?: number | null
  limit_date?: number | null
  feedback_way?: string | null
  fx_code: string
  in_use: string        // Y/N
  credit_card_index: number
  note?: string | null
}

export interface CreditCardCreate {
  credit_card_id: string
  card_name: string
  card_no?: string | null
  last_day?: number | null
  charge_day?: number | null
  limit_date?: number | null
  feedback_way?: string | null
  fx_code: string
  in_use?: string
  credit_card_index?: number
  note?: string | null
}

export type CreditCardUpdate = Partial<CreditCardCreate>

// ─── Monthly Report — Journal ────────────────────────────────────────────────
// Polymorphic FK constraints (enforced server-side):
//   spend_way_table  ↔ spend_way_type  ('Account' ↔ 'account', 'Credit_Card' ↔ 'credit_card')
//   action_main_table is always 'Code_Data' for UI writes
//   action_sub_* fields are populated together OR all null (no partial)

export interface Journal {
  distinct_number: number
  vesting_month: string         // YYYYMM
  spend_date: string            // YYYYMMDD
  spend_way: string
  spend_way_type: string        // 'account' | 'credit_card'
  spend_way_table: string       // 'Account' | 'Credit_Card'
  action_main: string
  action_main_type: string
  action_main_table: string     // 'Code_Data'
  action_sub?: string | null
  action_sub_type?: string | null
  action_sub_table?: string | null
  spending: number
  invoice_number?: string | null
  note?: string | null
}

export interface JournalCreate {
  vesting_month: string
  spend_date: string
  spend_way: string
  spend_way_type: string
  spend_way_table: string
  action_main: string
  action_main_type: string
  action_main_table: string
  action_sub?: string | null
  action_sub_type?: string | null
  action_sub_table?: string | null
  spending: number
  invoice_number?: string | null
  note?: string | null
}

export type JournalUpdate = Partial<JournalCreate>

export interface JournalListResponse {
  items: Journal[]
  gain_loss: number
}

// GET /monthly-report/journals/uncategorized-summary — journals whose
// action_main_type falls outside every report bucket (see utils/journalTypes.ts).
export interface UncategorizedMonthCount {
  vesting_month: string         // YYYYMM
  count: number
}

export interface UncategorizedSummary {
  total: number
  months: UncategorizedMonthCount[]  // newest first; zero months omitted
}

// ─── Monthly Report — Journal + Stock_Detail composite endpoint ──────────────
// POST /monthly-report/journals/stock-transaction writes a Journal row and a
// Stock_Detail row in a single transaction. excute_price is filled by the
// backend from journal.spending (sign preserved); account_id/account_name
// are resolved from journal.spend_way.

export interface StockTransactionDetailCreate {
  stock_id: string
  excute_type: 'buy' | 'sell' | 'stock' | 'cash'
  excute_amount?: number
  excute_date?: string | null
  memo?: string | null
}

export interface JournalStockTransactionCreate {
  journal: JournalCreate
  stock_detail: StockTransactionDetailCreate
}

export interface JournalStockTransactionUpdate {
  journal: JournalUpdate
  stock_detail: StockTransactionDetailCreate
}

export interface JournalStockTransactionRead {
  journal: Journal
  stock_detail: StockJournal
}

// ─── Monthly Report — Journal + Insurance_Journal composite endpoint ─────────
// Mirrors the stock composite. Insurance_Journal has no account columns, so
// there are no settling fields; excute_price is filled by the backend from
// journal.spending (sign preserved).

export interface InsuranceTransactionDetailCreate {
  insurance_id: string
  insurance_excute_type: 'pay' | 'cash' | 'return' | 'expect'
  excute_date?: string | null
  memo?: string | null
}

export interface JournalInsuranceTransactionCreate {
  journal: JournalCreate
  insurance_detail: InsuranceTransactionDetailCreate
}

export interface JournalInsuranceTransactionUpdate {
  journal: JournalUpdate
  insurance_detail: InsuranceTransactionDetailCreate
}

export interface JournalInsuranceTransactionRead {
  journal: Journal
  insurance_detail: InsuranceJournal
}

// ─── Monthly Report — Journal + Estate_Journal composite endpoint ────────────
// Same shape as the insurance composite.

export interface EstateTransactionDetailCreate {
  estate_id: string
  estate_excute_type: 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit'
  excute_date?: string | null
  memo?: string | null
}

export interface JournalEstateTransactionCreate {
  journal: JournalCreate
  estate_detail: EstateTransactionDetailCreate
}

export interface JournalEstateTransactionUpdate {
  journal: JournalUpdate
  estate_detail: EstateTransactionDetailCreate
}

export interface JournalEstateTransactionRead {
  journal: Journal
  estate_detail: EstateJournal
}

// Loan repayment composite: one payment splits into principal + interest, each
// stored as a positive-magnitude Loan_Journal row (so the Read returns a list).
export interface LoanTransactionDetailCreate {
  loan_id: string
  principal?: number
  interest?: number
  excute_date?: string | null
  memo?: string | null
}

export interface JournalLoanTransactionCreate {
  journal: JournalCreate
  loan_detail: LoanTransactionDetailCreate
}

export interface JournalLoanTransactionUpdate {
  journal: JournalUpdate
  loan_detail: LoanTransactionDetailCreate
}

export interface JournalLoanTransactionRead {
  journal: Journal
  loan_details: LoanJournal[]
}

export type SelectionStock = SelectionGroup
export type SelectionOtherAssetType = SelectionGroup

// ─── Monthly Report — Journal analytics ──────────────────────────────────────

export interface JournalExpenditureBudgetRow {
  action_main_type: string
  actual: number
  expected: number
  diff: number
  usage_rate: number
}

export interface JournalExpenditureBudget {
  rows: JournalExpenditureBudgetRow[]
}

export interface JournalRatioItem {
  name: string
  value: number
}

export interface JournalExpenditureRatio {
  outer: JournalRatioItem[]
  inner: JournalRatioItem[]
}

export interface JournalInvestRatio {
  items: JournalRatioItem[]
}

export interface JournalLiabilityItem {
  credit_card_id: string
  credit_card_name: string
  amount: number
}

export interface JournalLiability {
  items: JournalLiabilityItem[]
}

// ─── Monthly Report — Stock prices ───────────────────────────────────────────

export interface StockPriceEntry {
  stock_code: string
  stock_name: string
  close_price: number | null   // null when the requested month has no price row
  fetch_date: string | null    // YYYYMMDD of the row close_price came from, else null
}

// Insurance surrender value (解約金) recorded per policy per month. surrender_value
// is the latest recorded value on or before the month (carried forward); recorded
// is true only when entered in this exact month.
export interface InsuranceValueMonth {
  insurance_id: string
  insurance_name: string
  surrender_value: number | null
  vesting_month: string | null
  recorded: boolean
}

export interface InsuranceValueCreate {
  insurance_id: string
  vesting_month: string         // YYYYMM
  surrender_value: number
  memo?: string | null
}

// Real-estate market value (估值) recorded per property per month. market_value
// is the latest recorded value on or before the month (carried forward); recorded
// is true only when entered in this exact month.
export interface EstateValueMonth {
  estate_id: string
  estate_name: string
  market_value: number | null
  vesting_month: string | null
  recorded: boolean
}

export interface EstateValueCreate {
  estate_id: string
  vesting_month: string         // YYYYMM
  market_value: number
  memo?: string | null
}

// Index-based suggested market value (P3): cost × (current index / obtain-quarter
// index), from the 內政部 住宅價格指數 (market-based). Advisory — a recorded value
// always overrides it. suggested_market_value is null when the index is missing.
export interface EstateValueSuggestion {
  estate_id: string
  estate_name: string
  cost: number
  suggested_market_value: number | null
  region: string
  obtain_quarter: string | null
  current_quarter: string | null
}

export interface IndexRefreshResult {
  region: string
  upserted: number
  ok: boolean                   // false when the fetch failed and old data was kept
}

export type StockPriceRead = StockPriceEntry

export interface StockPriceHistory {
  stock_code: string
  fetch_date: string            // YYYYMMDD
  open_price: number
  highest_price: number
  lowest_price: number
  close_price: number
}

// ─── Monthly Report — Settle ─────────────────────────────────────────────────

export interface SettleResult {
  vesting_month: string
  estate_rows: number
  insurance_rows: number
  loan_rows: number
  stock_rows: number
  account_rows: number
  credit_card_rows: number
}

// ─── Assets — common detail/journal shape ────────────────────────────────────

export interface AssetDetailBase {
  distinct_number: number
  excute_price: number
  excute_date: string           // YYYYMMDD
  memo?: string | null
}

// ─── Assets — Stock ──────────────────────────────────────────────────────────

export interface StockAsset {
  stock_id: string
  stock_code: string
  stock_name: string
  asset_id: string
  expected_spend: number
  category_id?: string | null   // FK to StockCategory; null = unclassified
}

export interface StockAssetCreate {
  stock_id: string
  stock_code: string
  stock_name: string
  asset_id: string
  expected_spend: number
  category_id?: string | null
}

export type StockAssetUpdate = Partial<StockAssetCreate>

// Computed per-holding performance from GET /assets/stocks/summary. Money fields
// are in the holding's own fx_code (no base-currency conversion); percent/yield
// fields are fractions (0.05 = 5%) and null when their denominator is 0 or no
// price snapshot exists. `realized` is capital gains only (dividends excluded).
export interface StockPnlSummary {
  stock_id: string
  stock_code: string
  stock_name: string
  shares: number
  cost: number
  market_value: number | null
  realized: number
  dividends_total: number
  unrealized: number | null
  unrealized_pct: number | null
  cash_yield: number | null
  cost_yield: number | null
  fx_code: string
  close_price: number | null
  price_date: string | null
}

// ─── Assets — StockCategory (allocation dictionary) ──────────────────────────
// User-maintained classes (成長型 / 債券 / 類現金 / …) referenced by
// StockAsset.category_id. category_id is generated server-side (SC-NNN).

export interface StockCategory {
  category_id: string
  name: string
  in_use: string                // Y/N
  category_index: number
}

export interface StockCategoryCreate {
  name: string
  in_use?: string
  category_index?: number
}

export type StockCategoryUpdate = Partial<StockCategoryCreate>

export interface StockJournal extends AssetDetailBase {
  stock_id: string
  excute_type: string           // 'buy' | 'sell' | 'stock' | 'cash'
  excute_amount: number
  account_id: string
  account_name: string
}

export interface StockJournalCreate {
  stock_id: string
  excute_type: string
  excute_amount: number
  excute_price: number
  excute_date: string
  account_id: string
  account_name: string
  memo?: string | null
}

export type StockJournalUpdate = Partial<StockJournalCreate>

// ─── Assets — Estate ─────────────────────────────────────────────────────────

export interface EstateAsset {
  estate_id: string
  estate_name: string
  estate_type: string
  estate_address: string
  asset_id: string
  fx_code: string               // currency code (TWD; USD/JPY/... for overseas)
  obtain_date: string           // YYYYMMDD
  loan_id?: string | null
  estate_status: string         // 'idle' | 'live' | 'rent' | 'sold'
  region?: string | null        // house-price-index 縣市; null → 全國
  memo?: string | null
}

export interface EstateAssetCreate {
  estate_id: string
  estate_name: string
  estate_type: string
  estate_address: string
  asset_id: string
  fx_code?: string              // currency code; defaults to TWD on the backend
  obtain_date: string
  loan_id?: string | null
  estate_status: string
  region?: string | null        // house-price-index 縣市; null → 全國
  memo?: string | null
}

export type EstateAssetUpdate = Partial<EstateAssetCreate>

export interface EstateJournal extends AssetDetailBase {
  estate_id: string
  estate_excute_type: string    // 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit'
}

export interface EstateJournalCreate {
  estate_id: string
  estate_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type EstateJournalUpdate = Partial<EstateJournalCreate>

// ─── Assets — Insurance ──────────────────────────────────────────────────────

export interface InsuranceAsset {
  insurance_id: string
  insurance_name: string
  asset_id: string
  in_account: string
  out_account: string
  start_date: string            // YYYYMMDD
  end_date: string              // YYYYMMDD
  pay_type: string
  pay_day: string               // premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type
  expected_spend: number
  has_closed: string            // Y/N
}

export interface InsuranceAssetCreate {
  insurance_id: string
  insurance_name: string
  asset_id: string
  in_account: string
  out_account: string
  start_date: string
  end_date: string
  pay_type: string
  pay_day: string               // premium date(s); 'DD' / 'MM/DD' / 'MM/DD,...' by pay_type
  expected_spend: number
  has_closed: string
}

export type InsuranceAssetUpdate = Partial<InsuranceAssetCreate>

export interface InsuranceJournal extends AssetDetailBase {
  insurance_id: string
  insurance_excute_type: string // 'pay' | 'cash' | 'return' | 'expect'
}

export interface InsuranceJournalCreate {
  insurance_id: string
  insurance_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type InsuranceJournalUpdate = Partial<InsuranceJournalCreate>

// ─── Assets — Loan ───────────────────────────────────────────────────────────

export interface LoanAsset {
  loan_id: string
  loan_name: string
  loan_type: string
  account_id: string
  account_name: string
  interest_rate: number
  period: number
  apply_date: string            // YYYYMMDD
  grace_expire_date?: string | null
  pay_day: number
  amount: number
  repayed: number
  loan_index: number
}

export interface LoanAssetCreate {
  loan_id: string
  loan_name: string
  loan_type: string
  account_id: string
  account_name: string
  interest_rate: number
  period: number
  apply_date: string
  grace_expire_date?: string | null
  pay_day: number
  amount: number
  repayed: number
  loan_index: number
}

export type LoanAssetUpdate = Partial<LoanAssetCreate>

export interface LoanJournal extends AssetDetailBase {
  loan_id: string
  loan_excute_type: string      // 'principal' | 'interest' | 'increment' | 'fee'
}

export interface LoanJournalCreate {
  loan_id: string
  loan_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

export type LoanJournalUpdate = Partial<LoanJournalCreate>

export interface LoanSelection {
  loan_id: string
  loan_name: string
}

// ─── Assets — OtherAsset ─────────────────────────────────────────────────────

export interface OtherAsset {
  asset_id: string
  asset_name: string
  asset_type: string
  in_use: string                // Y/N
  asset_index: number
}

export interface OtherAssetCreate {
  asset_id: string
  asset_name: string
  asset_type: string
  in_use: string
  asset_index?: number
}

export type OtherAssetUpdate = Partial<OtherAssetCreate>

export interface OtherAssetItem {
  asset_type: string
}

// ─── Reports ─────────────────────────────────────────────────────────────────

export interface BalanceReportLine {
  name: string
  amount: number                // base-currency (TWD) equivalent
  original_amount: number       // amount in original currency (pre-FX)
  currency?: string
}

export interface BalanceReport {
  assets: {
    accounts: BalanceReportLine[]
    estates: BalanceReportLine[]
    insurances: BalanceReportLine[]
    stocks: BalanceReportLine[]
  }
  liabilities: {
    credit_cards: BalanceReportLine[]
    loans: BalanceReportLine[]
  }
  net_worth: number
}

export interface ExpenditureReportPoint {
  period: string                // YYYYMM or YYYY
  amount: number
}

export interface ExpenditureReport {
  type: string                  // 'monthly' | 'yearly'
  points: ExpenditureReportPoint[]
}

export interface IncomeExpensePoint {
  period: string                // YYYYMM or YYYY
  income: number                // positive
  fixed: number                 // fixed-expense magnitude, positive
  floating: number              // variable-expense magnitude, positive
  expense: number               // fixed + floating, positive
  net: number                   // income - expense (signed; negative = overspent)
  loan_repayment: number        // principal + interest cash outflow, positive; additive (not in expense/net)
}

export interface IncomeExpenseSummary {
  total_income: number
  total_expense: number
  net: number
  savings_rate: number          // net / total_income (0 when no income; may be negative)
}

export interface IncomeExpenseReport {
  type: string                  // 'monthly' | 'yearly'
  points: IncomeExpensePoint[]
  summary: IncomeExpenseSummary
}

// Retirement readiness (consumption-basis FIRE target + debt-service health).
export interface RetirementSetting {
  withdrawal_rate: number             // decimal, e.g. 0.04
  annual_expense_override: number | null
  exclude_self_occupied_estate: boolean  // exclude estate_status 'live' from net worth
}

export type RetirementSettingUpdate = Partial<RetirementSetting>

export interface LoanPayoff {
  loan_id: string
  loan_name: string
  remaining_balance: number           // TWD, positive
  monthly_payment: number             // recent avg principal+interest, TWD
  payoff_month: string | null         // YYYYMM, null if unknown
  years_left: number | null
}

export interface RetirementReadiness {
  net_worth: number                   // self-occupied housing excluded when configured
  exclude_self_occupied_estate: boolean
  self_occupied_estate_value: number  // amount excluded; 0 when off or none marked 'live'
  annual_expense_base: number
  expense_base_source: 'computed' | 'override'
  withdrawal_rate: number
  target_portfolio: number
  readiness_pct: number               // net_worth / target (≥1 = reached)
  gap: number                         // target − net_worth
  monthly_income: number
  monthly_loan_payment: number
  debt_service_ratio: number          // monthly_loan_payment / monthly_income
  loans: LoanPayoff[]
}

// Comprehensive income statement (綜合損益表): 本業 / 投資 / 綜合. Magnitudes
// (active_income/fixed/floating/dividend) are positive; *_net and realized/
// unrealized are signed (negative = loss). Distinct from IncomeExpense: active
// income excludes passive (孳息), which moves into the investment section.
export interface IncomeStatementPoint {
  period: string                // YYYYMM or YYYY
  active_income: number         // 本業收入 (income type only), positive
  fixed: number                 // fixed-expense magnitude, positive
  floating: number              // variable-expense magnitude, positive
  loan_interest: number         // 貸款利息 (Loan_Journal interest/fee), positive
  operating_net: number         // active_income - fixed - floating - loan_interest (signed)
  dividend: number              // 孳息 (passive income), positive
  realized: number              // 已實現資本利得 (signed)
  unrealized: number            // 未實現市值變動 (signed)
  investment_net: number        // dividend + realized + unrealized (signed)
  comprehensive_net: number     // operating_net + investment_net (signed)
}

export interface IncomeStatementSummary {
  active_income: number
  fixed: number
  floating: number
  loan_interest: number
  operating_net: number
  dividend: number
  realized: number
  unrealized: number
  investment_net: number
  comprehensive_net: number
}

export interface IncomeStatementReport {
  type: string                  // 'monthly' | 'yearly'
  points: IncomeStatementPoint[]
  summary: IncomeStatementSummary
}

export interface ExpenditureSubNode {
  code: string                  // action_sub code_id ('' = un-subcategorized remainder)
  name: string
  amount: number
  share: number                 // % of grand total expense
}

export interface ExpenditureCategoryNode {
  code: string                  // action_main code_id
  name: string
  type: string                  // 'Fixed' | 'Floating'
  amount: number
  share: number                 // % of grand total expense
  children: ExpenditureSubNode[]
}

export interface ExpenditureComposition {
  total: number
  fixed_total: number
  floating_total: number
  categories: ExpenditureCategoryNode[]
}

export interface BudgetVarianceRow {
  code: string
  name: string
  type: string                  // 'Fixed' | 'Floating'
  expected: number
  actual: number
  diff: number                  // actual - expected (positive = over budget)
  usage_rate: number            // actual / expected (0 when no budget)
}

export interface BudgetVarianceSummary {
  total_expected: number
  total_actual: number
  total_diff: number
  usage_rate: number
  elapsed_months: number        // latest month (1-12) with data; drives projection
  projected_total: number       // run-rate annualized actual
}

export interface BudgetVariance {
  year: string
  rows: BudgetVarianceRow[]
  summary: BudgetVarianceSummary
}

export interface CashFlowItem {
  label: string
  amount: number                // signed (positive = cash in, negative = cash out)
}

export interface CashFlowActivity {
  key: string                   // 'operating' | 'investing' | 'financing'
  label: string                 // 生活 / 投資 / 債務
  net: number
  items: CashFlowItem[]
}

export interface CashFlowPoint {
  period: string                // YYYYMM or YYYY
  operating: number             // 生活 net (income - living - loan interest), signed
  investing: number             // 投資 net (buy negative, sell positive), signed
  financing: number             // 債務 net (new borrowing - principal repayment), signed
  net_change: number            // operating + investing + financing, signed
}

export interface CashFlowSummary {
  activities: CashFlowActivity[]
  net_change: number
}

export interface CashFlow {
  type: string                  // 'monthly' | 'yearly'
  points: CashFlowPoint[]
  summary: CashFlowSummary
}

export interface YoYRow {
  code: string
  name: string
  type: string                  // 'Fixed' | 'Floating'
  current: number
  previous: number
  delta: number                 // current - previous
  yoy_rate: number              // (current - previous) / previous (0 when previous == 0)
}

export interface LargeTxn {
  date: string                  // YYYYMMDD
  category: string
  amount: number
  pay_way: string
  note: string | null
}

export interface ExpenseInsights {
  year: string
  yoy: YoYRow[]
  largest: LargeTxn[]
}

export interface AssetReportItem {
  type: string
  amount: number
  share: number
}

export interface AssetReport {
  total: number
  items: AssetReportItem[]
}

export interface StockAllocationReportItem {
  category_id: string | null    // null = unclassified bucket
  category_name: string         // '未分類' for the unclassified bucket
  amount: number
  share: number                 // percentage 0-100
}

export interface StockAllocationReport {
  total: number
  items: StockAllocationReportItem[]
}

// ─── Dashboard ───────────────────────────────────────────────────────────────

export interface DashboardSummaryPoint {
  period: string                // YYYYMM
  value: number
  breakdown?: Record<string, number>
}

export interface DashboardSummary {
  type: string
  points: DashboardSummaryPoint[]
}

export interface DashboardAlarm {
  date: string            // YYYYMMDD expanded occurrence
  content: string
  alarm_type: AlarmType   // 'Y' yearly, 'M' monthly
}

export interface DashboardBudgetLine {
  category: string
  planned: number
  actual: number
  usage_pct: number
}

export interface DashboardBudget {
  type: string                  // 'monthly' | 'yearly'
  period: string                // YYYYMM | YYYY
  lines: DashboardBudgetLine[]
  total_planned: number
  total_actual: number
  event_lines: DashboardBudgetLine[]   // annual-event categories (envelope vs YTD)
  event_total_planned: number
  event_total_actual: number
}

export interface DashboardGift {
  owner: string
  amount: number
  rate: number
}

export interface TargetSetting {
  distinct_number: string
  target_year: string           // YYYY
  setting_value: string         // Free-form target description / value
  is_done: string               // Y/N
}

export interface TargetSettingCreate {
  // distinct_number is auto-assigned by the backend (sequential)
  setting_value: string
  target_year?: string
  is_done?: string
}

export interface TargetSettingUpdate {
  target_year?: string
  setting_value?: string
  is_done?: string
}

// ─── Utilities — Selections (grouped responses) ──────────────────────────────
// All /utilities/selections/* endpoints return SelectionGroup[].
// These aliases exist so per-domain consumers can import a clearly-named type.

export type SelectionAccount = SelectionGroup
export type SelectionCode = SelectionGroup
export type SelectionCreditCard = SelectionGroup
export type SelectionEstate = SelectionGroup
export type SelectionInsurance = SelectionGroup
export type SelectionLoan = SelectionGroup

// ─── Utilities — Import ──────────────────────────────────────────────────────

export interface ImportResult {
  message: string
}

export interface InvoiceImportError {
  line: number
  reason: string
}

export interface InvoiceImportMonth {
  month: string
  imported: number
  skipped: number
}

export interface InvoiceImportResult {
  imported: number
  skipped: number
  failed: number
  months: InvoiceImportMonth[]
  errors: InvoiceImportError[]
}
