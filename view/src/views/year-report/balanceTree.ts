/**
 * Balance-sheet tree builders.
 *
 * Turns the flat `BalanceReport` (every entity as its own line) into the
 * category → currency/market sub-group → entity hierarchy the page renders.
 *
 * Accounting notes:
 * - `line.amount` is already FX-converted to base currency (TWD); summing
 *   across lines is therefore correct. `line.original_amount` keeps the
 *   pre-FX native figure, shown only for foreign-currency groups/leaves.
 * - Stocks carry no market field, so 台股/美股 is derived from the holding's
 *   original currency as a proxy (TWD → 台股, USD → 美股).
 * - Liabilities may be stored signed (negative in real data, positive in
 *   mock); magnitudes use Math.abs so totals/shares are convention-agnostic.
 */
import type { BalanceReport, BalanceReportLine } from '@/types/models'
import { i18n } from '@/i18n'

export interface BalanceNode {
  key: string
  label: string
  amount: number // TWD-equivalent subtotal (signed as provided)
  share?: number // % of total assets / total liabilities
  originalAmount?: number // only when the node is a single foreign currency
  originalCurrency?: string // e.g. 'USD'; omitted when TWD
  children?: BalanceNode[]
}

const BASE_CURRENCY = 'TWD'

// Friendly labels for common currencies; any code not listed falls back to the
// raw code (e.g. 'SGD'), so multi-currency support is not limited to this list.
const CURRENCY_LABEL: Record<string, string> = {
  TWD: 'balanceSheet.curTWD',
  USD: 'balanceSheet.curUSD',
  JPY: 'balanceSheet.curJPY',
  EUR: 'balanceSheet.curEUR',
  CNY: 'balanceSheet.curCNY',
  HKD: 'balanceSheet.curHKD',
  GBP: 'balanceSheet.curGBP',
  AUD: 'balanceSheet.curAUD',
}

// Stock market labels via the currency proxy; unlisted codes fall back to
// `<code> 股` (e.g. 'SGD 股').
const MARKET_LABEL: Record<string, string> = {
  TWD: 'balanceSheet.mktTWD',
  USD: 'balanceSheet.mktUSD',
  JPY: 'balanceSheet.mktJPY',
  HKD: 'balanceSheet.mktHKD',
  CNY: 'balanceSheet.mktCNY',
  EUR: 'balanceSheet.mktEUR',
}

function currencyOf(line: BalanceReportLine): string {
  return line.currency ?? BASE_CURRENCY
}

export function sumLeaves(lines: BalanceReportLine[]): number {
  return lines.reduce((s, l) => s + l.amount, 0)
}

export function totalAssets(report: BalanceReport): number {
  const a = report.assets
  return sumLeaves([...a.accounts, ...a.stocks, ...a.insurances, ...a.estates])
}

export function totalLiabilities(report: BalanceReport): number {
  const l = report.liabilities
  return [...l.credit_cards, ...l.loans].reduce((s, x) => s + Math.abs(x.amount), 0)
}

function leafNode(line: BalanceReportLine, keyPrefix: string, idx: number): BalanceNode {
  const cur = currencyOf(line)
  const node: BalanceNode = {
    key: `${keyPrefix}-leaf-${idx}`,
    label: line.name,
    amount: line.amount,
  }
  if (cur !== BASE_CURRENCY) {
    node.originalAmount = line.original_amount
    node.originalCurrency = cur
  }
  return node
}

/** Group lines into one sub-group node per original currency (first-seen order). */
function groupByCurrency(
  lines: BalanceReportLine[],
  keyPrefix: string,
  labelMap: Record<string, string>,
  labelFallback: (code: string) => string,
): BalanceNode[] {
  const order: string[] = []
  const buckets = new Map<string, BalanceReportLine[]>()
  for (const line of lines) {
    const cur = currencyOf(line)
    if (!buckets.has(cur)) {
      buckets.set(cur, [])
      order.push(cur)
    }
    buckets.get(cur)!.push(line)
  }

  return order.map((cur) => {
    const groupLines = buckets.get(cur)!
    const groupKey = `${keyPrefix}-${cur}`
    const node: BalanceNode = {
      key: groupKey,
      label: labelMap[cur] ? i18n.global.t(labelMap[cur]) : labelFallback(cur),
      amount: sumLeaves(groupLines),
      children: groupLines.map((l, i) => leafNode(l, groupKey, i)),
    }
    if (cur !== BASE_CURRENCY) {
      node.originalAmount = groupLines.reduce((s, l) => s + l.original_amount, 0)
      node.originalCurrency = cur
    }
    return node
  })
}

function categoryNode(
  key: string,
  label: string,
  lines: BalanceReportLine[],
  children: BalanceNode[],
  share: (amount: number) => number,
): BalanceNode {
  const amount = sumLeaves(lines)

  // Collapse a pointless single-currency layer: when grouping produced exactly
  // one sub-group, promote its leaves so the category lists entities directly.
  let finalChildren = children
  if (children.length === 1 && children[0]!.children) {
    finalChildren = children[0]!.children!
  } else {
    // Share belongs on sub-group rows (level 2), not on individual leaves.
    finalChildren = children.map((c) =>
      c.children ? { ...c, share: share(c.amount) } : c,
    )
  }

  return { key, label, amount, share: share(amount), children: finalChildren }
}

export function buildAssetTree(report: BalanceReport): BalanceNode[] {
  const a = report.assets
  const total = totalAssets(report)
  const share = (amount: number) => (total ? (amount / total) * 100 : 0)

  const nodes: BalanceNode[] = []
  // Liquidity order: cash → investments → insurance → real estate.
  if (a.accounts.length) {
    nodes.push(
      categoryNode(
        'cash',
        i18n.global.t('balanceSheet.catCash'),
        a.accounts,
        groupByCurrency(a.accounts, 'cash', CURRENCY_LABEL, (c) => c),
        share,
      ),
    )
  }
  if (a.stocks.length) {
    nodes.push(
      categoryNode(
        'stock',
        i18n.global.t('balanceSheet.catInvest'),
        a.stocks,
        groupByCurrency(a.stocks, 'stock', MARKET_LABEL, (c) =>
          i18n.global.t('balanceSheet.mktFallback', { code: c }),
        ),
        share,
      ),
    )
  }
  if (a.insurances.length) {
    // Insurance carries a real currency (e.g. USD 儲蓄險), so group by currency
    // like accounts. The single-currency collapse keeps all-TWD policies flat.
    nodes.push(
      categoryNode(
        'insurance',
        i18n.global.t('balanceSheet.catInsurance'),
        a.insurances,
        groupByCurrency(a.insurances, 'insurance', CURRENCY_LABEL, (c) => c),
        share,
      ),
    )
  }
  if (a.estates.length) {
    // Estates can be foreign (overseas property), so group by currency too.
    nodes.push(
      categoryNode(
        'estate',
        i18n.global.t('balanceSheet.catEstate'),
        a.estates,
        groupByCurrency(a.estates, 'estate', CURRENCY_LABEL, (c) => c),
        share,
      ),
    )
  }
  return nodes
}

export function buildLiabilityTree(report: BalanceReport): BalanceNode[] {
  const l = report.liabilities
  const total = totalLiabilities(report)
  const share = (amount: number) => (total ? (Math.abs(amount) / total) * 100 : 0)

  const nodes: BalanceNode[] = []
  // Maturity order: current (credit cards) → long-term (loans).
  if (l.credit_cards.length) {
    const amount = sumLeaves(l.credit_cards)
    nodes.push({
      key: 'cc',
      label: i18n.global.t('balanceSheet.catCreditCard'),
      amount,
      share: share(amount),
      children: l.credit_cards.map((x, i) => leafNode(x, 'cc', i)),
    })
  }
  if (l.loans.length) {
    // Loans can be foreign (currency follows the repayment account).
    nodes.push(
      categoryNode(
        'loan',
        i18n.global.t('balanceSheet.catLoan'),
        l.loans,
        groupByCurrency(l.loans, 'loan', CURRENCY_LABEL, (c) => c),
        share,
      ),
    )
  }
  return nodes
}
