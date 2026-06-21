// 現金流量表 (Cash flow statement) page.
export default {
  title: 'Cash Flow Statement',
  subtitle: 'FY{year} · Operating / Investing / Financing',
  empty: 'No cash flow data',
  operatingNet: 'Operating Net',
  operatingTooltip: 'Income − living expenses − loan interest',
  investingNet: 'Investing Net',
  investingTooltip: 'Net investment trades (buys negative, sells positive)',
  financingNet: 'Financing Net',
  financingTooltip: 'New borrowing − principal repaid',
  netChange: 'Net Cash Change',
  netChangeTooltip: 'Operating + Investing + Financing',
  composition: 'Cash Flow Composition (Operating → Investing → Financing)',
  byPeriod: 'Cash Flow by Period',
  detail: 'Cash Flow Detail',
  detailNote:
    'Self-transfers are excluded; credit card spending is counted once in the month of purchase. Investment trades and debt principal are cash flows, intentionally different from the P/L basis of the "Income Statement" — not an error.',
  seriesOperating: 'Operating',
  seriesInvesting: 'Investing',
  seriesFinancing: 'Financing',
}
