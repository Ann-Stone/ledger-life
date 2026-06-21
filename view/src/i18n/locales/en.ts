// English (en) — merges every per-domain module into one message tree.
// Must stay key-for-key identical to zh-TW.ts (enforced by the locale parity test).
import common from './en/common'
import nav from './en/nav'
import route from './en/route'
import toast from './en/toast'
import validation from './en/validation'
import selection from './en/selection'
import financialBehavior from './en/financialBehavior'
import noteHints from './en/noteHints'
import cashFlow from './en/cashFlow'
import notFound from './en/notFound'
import balanceSheet from './en/balanceSheet'
import incomeStatement from './en/incomeStatement'
import cashFlowStatement from './en/cashFlowStatement'
import spending from './en/spending'
import asset from './en/asset'
import dashboard from './en/dashboard'
import forms from './en/forms'
import settingBudget from './en/settingBudget'
import settingMenu from './en/settingMenu'
import settingRemind from './en/settingRemind'
import otherAssets from './en/otherAssets'
import importMessages from './en/import'
import chart from './en/chart'
import alarm from './en/alarm'

export default {
  common,
  nav,
  route,
  toast,
  validation,
  selection,
  financialBehavior,
  noteHints,
  cashFlow,
  notFound,
  balanceSheet,
  incomeStatement,
  cashFlowStatement,
  spending,
  asset,
  dashboard,
  forms,
  settingBudget,
  settingMenu,
  settingRemind,
  otherAssets,
  import: importMessages,
  chart,
  alarm,
}
