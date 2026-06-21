// Traditional Chinese (zh-TW) — merges every per-domain module into one message tree.
// Add new page modules here as they are created during the page-by-page sweep.
import common from './zh-TW/common'
import nav from './zh-TW/nav'
import route from './zh-TW/route'
import toast from './zh-TW/toast'
import validation from './zh-TW/validation'
import selection from './zh-TW/selection'
import financialBehavior from './zh-TW/financialBehavior'
import noteHints from './zh-TW/noteHints'
import cashFlow from './zh-TW/cashFlow'
import notFound from './zh-TW/notFound'
import balanceSheet from './zh-TW/balanceSheet'
import incomeStatement from './zh-TW/incomeStatement'
import cashFlowStatement from './zh-TW/cashFlowStatement'
import spending from './zh-TW/spending'
import asset from './zh-TW/asset'
import dashboard from './zh-TW/dashboard'
import forms from './zh-TW/forms'
import settingBudget from './zh-TW/settingBudget'
import settingMenu from './zh-TW/settingMenu'
import settingRemind from './zh-TW/settingRemind'
import otherAssets from './zh-TW/otherAssets'
import importMessages from './zh-TW/import'
import chart from './zh-TW/chart'
import alarm from './zh-TW/alarm'
import retirement from './zh-TW/retirement'

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
  retirement,
}
