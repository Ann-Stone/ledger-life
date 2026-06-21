import { createRouter, createWebHistory } from 'vue-router'
import { watch } from 'vue'
import { i18n } from '@/i18n'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/dashboard',
    },
    {
      path: '/',
      component: () => import('@/components/layout/AppLayout.vue'),
      children: [
        {
          path: 'dashboard',
          name: 'Dashboard',
          component: () => import('@/views/DashboardView.vue'),
          meta: { titleKey: 'route.dashboard' },
        },
        // Monthly Report
        {
          path: 'monthly-report/cash-flow',
          name: 'CashFlow',
          component: () => import('@/views/monthly-report/CashFlowView.vue'),
          meta: { titleKey: 'route.cashFlow', breadcrumbKeys: ['route.cashFlow'] },
        },
        // Year Report
        {
          path: 'year-report/balance-sheet',
          name: 'BalanceSheet',
          component: () => import('@/views/year-report/BalanceSheetView.vue'),
          meta: { titleKey: 'route.balanceSheet', breadcrumbKeys: ['route.reports', 'route.balanceSheet'] },
        },
        {
          path: 'year-report/income-statement',
          name: 'IncomeStatement',
          component: () => import('@/views/year-report/IncomeStatementView.vue'),
          meta: { titleKey: 'route.incomeStatement', breadcrumbKeys: ['route.reports', 'route.incomeStatement'] },
        },
        {
          path: 'year-report/cash-flow-statement',
          name: 'CashFlowStatement',
          component: () => import('@/views/year-report/CashFlowStatementView.vue'),
          meta: { titleKey: 'route.cashFlowStatement', breadcrumbKeys: ['route.reports', 'route.cashFlowStatement'] },
        },
        {
          path: 'year-report/spending',
          name: 'Spending',
          component: () => import('@/views/year-report/SpendingView.vue'),
          meta: { titleKey: 'route.spending', breadcrumbKeys: ['route.reports', 'route.spending'] },
        },
        {
          path: 'year-report/assets',
          name: 'Assets',
          component: () => import('@/views/year-report/AssetView.vue'),
          meta: { titleKey: 'route.assets', breadcrumbKeys: ['route.reports', 'route.assets'] },
        },
        // Other Assets & Liabilities
        {
          path: 'other-assets',
          name: 'OtherAssets',
          component: () => import('@/views/other-assets/OtherAssetsView.vue'),
          meta: { titleKey: 'route.otherAssets' },
        },
        // Settings
        {
          path: 'setting/menu',
          name: 'SettingMenu',
          component: () => import('@/views/setting/MenuSettingView.vue'),
          meta: { titleKey: 'route.settingMenu', breadcrumbKeys: ['route.settings', 'route.settingMenuLeaf'] },
        },
        {
          path: 'setting/budget',
          name: 'SettingBudget',
          component: () => import('@/views/setting/BudgetSettingView.vue'),
          meta: { titleKey: 'route.settingBudget', breadcrumbKeys: ['route.settings', 'route.settingBudgetLeaf'] },
        },
        {
          path: 'setting/remind',
          name: 'SettingRemind',
          component: () => import('@/views/setting/RemindSettingView.vue'),
          meta: { titleKey: 'route.settingRemind', breadcrumbKeys: ['route.settings', 'route.settingRemindLeaf'] },
        },
        // Utilities
        {
          path: 'utilities/import',
          name: 'UtilitiesImport',
          component: () => import('@/views/utilities/ImportView.vue'),
          meta: { titleKey: 'route.import', breadcrumbKeys: ['route.utilities', 'route.import'] },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('@/views/NotFoundView.vue'),
    },
  ],
})

// Update document title on route change and re-translate when the locale changes.
function applyTitle(to = router.currentRoute.value) {
  const key = (to.meta as { titleKey?: string }).titleKey
  const appName = i18n.global.t('route.appName')
  document.title = key ? `${i18n.global.t(key)} — ${appName}` : appName
}

router.afterEach((to) => applyTitle(to))
watch(i18n.global.locale, () => applyTitle())

export default router
