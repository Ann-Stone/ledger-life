/**
 * CSS-var–driven chart colour helper.
 * Reads current design-system tokens at call time so the palette
 * automatically adapts when the html.dark / html.light class changes.
 */
export function getChartColors(): string[] {
  const isDark = typeof document !== 'undefined' && document.documentElement.classList.contains('dark')
  
  if (isDark) {
    return [
      '#a78bfa', // 保險: soft purple (indigo-400)
      '#fca5a5', // 不動產: warm peach (red-300)
      '#34d399', // 股票: emerald green (emerald-400)
      '#60a5fa', // 現金: sky blue (blue-400)
      '#f472b6', // 信用卡: soft pink (pink-400)
      '#fbbf24', // 貸款: amber gold (amber-400)
    ]
  } else {
    return [
      '#6d28d9', // 保險: deep indigo (indigo-700)
      '#be123c', // 不動產: rich rose (rose-700)
      '#047857', // 股票: deep emerald (emerald-700)
      '#1d4ed8', // 現金: deep blue (blue-700)
      '#be185d', // 信用卡: vibrant pink (pink-700)
      '#b45309', // 貸款: warm amber (amber-700)
    ]
  }
}
