<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('spending.title')" :subtitle="t('common.yearLabel', { year: store.selectedYear })">
      <template #actions>
        <el-date-picker
          v-model="selectedYearDate"
          type="year"
          :placeholder="t('common.pickYear')"
          format="YYYY"
          :clearable="false"
        />
      </template>
    </PageHeader>

    <el-tabs v-model="activeType" @tab-change="handleTypeChange">
      <el-tab-pane :label="t('common.monthly')" name="monthly" />
      <el-tab-pane :label="t('common.yearly')" name="yearly" />
    </el-tabs>

    <el-skeleton v-if="store.incomeExpenseLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" :message="t('spending.empty')" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        <MetricCard :label="t('spending.totalIncome')" :amount="summary.total_income" />
        <MetricCard :label="t('spending.totalExpense')" :amount="summary.total_expense" tone="rose" />
        <MetricCard
          :label="t('spending.netBalance')"
          :amount="summary.net"
          :tone="summary.net < 0 ? 'rose' : 'primary'"
        />
        <MetricCard
          :label="t('spending.savingsRate')"
          :amount="savingsRatePct"
          format="percent"
          signed
          :tone="summary.net < 0 ? 'rose' : 'primary'"
          :tooltip="t('spending.savingsRateTooltip')"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.incomeVsExpense')" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.expenseStructure')" />
        <el-skeleton v-if="store.compositionLoading" :rows="5" animated />
        <EmptyState
          v-else-if="!composition || composition.categories.length === 0"
          :message="t('spending.noExpenseDetail')"
        />
        <template v-else>
          <div class="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <MetricCard
              :label="t('spending.fixedExpenseCard')"
              :amount="composition.fixed_total"
              :delta-label="t('spending.shareOfExpense', { pct: fixedShare.toFixed(0) })"
              :tooltip="t('spending.fixedTooltip')"
            />
            <MetricCard
              :label="t('spending.floatingExpense')"
              :amount="composition.floating_total"
              :delta-label="t('spending.shareOfExpense', { pct: floatingShare.toFixed(0) })"
            />
            <MetricCard
              :label="t('spending.fixedToIncome')"
              :amount="fixedToIncomePct"
              format="percent"
              :tone="fixedToIncomePct > 50 ? 'rose' : 'primary'"
              :tooltip="t('spending.fixedToIncomeTooltip')"
            />
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table
              :data="expenditureTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" :label="t('common.item')" min-width="200">
                <template #default="{ row }">
                  <span>{{ row.label }}</span>
                  <el-tag
                    v-if="row.type"
                    :type="typeTagType(row.type)"
                    size="small"
                    effect="plain"
                    class="ml-2"
                  >
                    {{ typeLabel(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.amount')" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" currency="TWD" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('spending.share')" width="84" align="right">
                <template #default="{ row }">
                  <SharePercent :value="row.share" class="text-sm text-on-surface-variant" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.budgetVsActual')" />
        <el-skeleton v-if="store.budgetLoading" :rows="4" animated />
        <EmptyState
          v-else-if="!budget || budget.rows.length === 0"
          :message="t('spending.noBudget')"
        />
        <template v-else>
          <div class="flex flex-wrap items-center gap-x-8 gap-y-2 text-sm">
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">{{ t('spending.annualBudget') }}</span>
              <MoneyDisplay :amount="budget.summary.total_expected" currency="TWD" size="sm" />
            </div>
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">{{ t('spending.actual') }}</span>
              <MoneyDisplay :amount="budget.summary.total_actual" currency="TWD" size="sm" />
              <span class="text-on-surface-variant/70 tabular-nums">
                {{ (budget.summary.usage_rate * 100).toFixed(0) }}%
              </span>
            </div>
            <div class="flex items-center gap-2">
              <span class="text-on-surface-variant">{{ t('spending.projectedFull') }}</span>
              <MoneyDisplay
                :amount="budget.summary.projected_total"
                currency="TWD"
                size="sm"
                :positive="budget.summary.projected_total <= budget.summary.total_expected"
              />
              <span
                v-if="budget.summary.elapsed_months > 0 && budget.summary.elapsed_months < 12"
                class="text-on-surface-variant/60 text-xs"
              >
                {{ t('spending.projectedHint', { months: budget.summary.elapsed_months }) }}
              </span>
            </div>
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="budget.rows" row-key="code" border style="width: 100%">
              <el-table-column prop="name" :label="t('common.category')" min-width="160">
                <template #default="{ row }">
                  <span>{{ row.name }}</span>
                  <el-tag
                    v-if="row.type"
                    :type="typeTagType(row.type)"
                    size="small"
                    effect="plain"
                    class="ml-2"
                  >
                    {{ typeLabel(row.type) }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column :label="t('spending.colBudget')" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.expected" currency="TWD" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('spending.actual')" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.actual" currency="TWD" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('spending.colDiff')" width="130" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.diff" currency="TWD" size="sm" :positive="row.diff <= 0" />
                </template>
              </el-table-column>
              <el-table-column :label="t('spending.colUsage')" min-width="170">
                <template #default="{ row }">
                  <div class="flex items-center gap-2">
                    <el-progress
                      :percentage="Math.min(Math.round(row.usage_rate * 100), 100)"
                      :status="usageStatus(row.usage_rate)"
                      :show-text="false"
                      :stroke-width="8"
                      class="flex-1"
                    />
                    <span
                      class="tabular-nums text-xs w-12 text-right"
                      :class="row.usage_rate > 1 ? 'text-secondary' : 'text-on-surface-variant'"
                    >
                      {{ (row.usage_rate * 100).toFixed(0) }}%
                    </span>
                  </div>
                </template>
              </el-table-column>
            </el-table>
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.cashFlowSection')" />
        <el-skeleton v-if="store.cashFlowLoading" :rows="4" animated />
        <EmptyState v-else-if="!cashFlow" :message="t('spending.noCashFlow')" />
        <template v-else>
          <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
            <MetricCard
              v-for="act in cashFlow.summary.activities"
              :key="act.key"
              :label="act.label"
              :amount="act.net"
              :tone="act.net < 0 ? 'rose' : 'primary'"
              :tooltip="cfTooltip(act)"
            />
            <MetricCard
              :label="t('spending.netCashChange')"
              :amount="cashFlow.summary.net_change"
              :tone="cashFlow.summary.net_change < 0 ? 'rose' : 'primary'"
            />
          </div>
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <WaterfallChart :items="waterfallItems" :total-label="t('spending.netChangeLabel')" height="320px" />
          </div>
        </template>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.yoySection')" />
        <el-skeleton v-if="store.insightsLoading" :rows="3" animated />
        <EmptyState
          v-else-if="!insights || insights.yoy.length === 0"
          :message="t('spending.noYoy')"
        />
        <div v-else class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table :data="insights.yoy" row-key="code" border style="width: 100%">
            <el-table-column prop="name" :label="t('common.category')" min-width="140">
              <template #default="{ row }">
                <span>{{ row.name }}</span>
                <el-tag
                  v-if="row.type"
                  :type="typeTagType(row.type)"
                  size="small"
                  effect="plain"
                  class="ml-2"
                >
                  {{ typeLabel(row.type) }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column :label="t('spending.colCurrent')" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.current" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column :label="t('spending.colPrevious')" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.previous" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column :label="t('spending.colDelta')" width="130" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.delta" currency="TWD" size="sm" :positive="row.delta <= 0" />
              </template>
            </el-table-column>
            <el-table-column :label="t('spending.colYoyRate')" width="100" align="right">
              <template #default="{ row }">
                <span class="tabular-nums text-sm" :class="yoyClass(row.delta)">
                  {{ yoyRateText(row) }}
                </span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('spending.topSpending')" />
        <el-skeleton v-if="store.insightsLoading" :rows="3" animated />
        <EmptyState
          v-else-if="!insights || insights.largest.length === 0"
          :message="t('spending.noTransactions')"
        />
        <div v-else class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table :data="insights.largest" border style="width: 100%">
            <el-table-column :label="t('spending.colDate')" width="120">
              <template #default="{ row }">{{ fmtDate(row.date) }}</template>
            </el-table-column>
            <el-table-column prop="category" :label="t('common.category')" min-width="100" />
            <el-table-column :label="t('common.amount')" width="140" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" currency="TWD" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="pay_way" :label="t('spending.colPayWay')" min-width="120" />
            <el-table-column :label="t('common.note')" min-width="140">
              <template #default="{ row }">
                <span :class="row.note ? '' : 'text-on-surface-variant/40'">{{ row.note || '—' }}</span>
              </template>
            </el-table-column>
          </el-table>
        </div>
      </section>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SharePercent from '@/components/ui/SharePercent.vue'
import BarChart from '@/components/charts/BarChart.vue'
import WaterfallChart from '@/components/charts/WaterfallChart.vue'
import { useYearReportStore } from '@/stores/yearReport'
import { useMoney } from '@/composables/useMoney'
import { useYearDatePicker } from '@/composables/useYearDatePicker'
import { buildExpenditureTree } from './expenditureTree'
import type { CashFlowActivity } from '@/types/models'

const store = useYearReportStore()
const { t } = useI18n()
const { format: formatMoney } = useMoney()

const activeType = ref<'monthly' | 'yearly'>('monthly')

function reload() {
  void store.fetchIncomeExpenseReport(activeType.value, store.selectedYear)
  void store.fetchExpenditureComposition(activeType.value, store.selectedYear)
  void store.fetchBudgetVariance(store.selectedYear)
  void store.fetchCashFlow(activeType.value, store.selectedYear)
  void store.fetchExpenseInsights(store.selectedYear)
}

function handleTypeChange() {
  reload()
}

const { selectedYearDate } = useYearDatePicker({
  current: () => store.selectedYear,
  onChange: (year) => {
    store.selectedYear = year
    reload()
  },
})

onMounted(reload)

const hasData = computed(
  () => !!store.incomeExpenseReport && store.incomeExpenseReport.points.length > 0,
)

const summary = computed(
  () =>
    store.incomeExpenseReport?.summary ?? {
      total_income: 0,
      total_expense: 0,
      net: 0,
      savings_rate: 0,
    },
)

const savingsRatePct = computed(() => summary.value.savings_rate * 100)

const chart = computed(() => {
  const report = store.incomeExpenseReport
  if (!report) return { xData: [], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      { name: t('spending.seriesIncome'), data: report.points.map((p) => p.income) },
      // Fixed (the burn floor) at the bottom, variable stacked on top, so each
      // month's bar shows the locked-in floor vs the flexible part.
      { name: t('spending.seriesFixed'), data: report.points.map((p) => p.fixed), stack: 'expense' },
      { name: t('spending.floatingExpense'), data: report.points.map((p) => p.floating), stack: 'expense' },
      {
        name: t('spending.seriesNet'),
        data: report.points.map((p) => p.net),
        type: 'line' as const,
      },
    ],
  }
})

const composition = computed(() => store.compositionReport)

const expenditureTree = computed(() =>
  store.compositionReport ? buildExpenditureTree(store.compositionReport) : [],
)

const fixedShare = computed(() => {
  const c = store.compositionReport
  return c && c.total ? (c.fixed_total / c.total) * 100 : 0
})

const floatingShare = computed(() => {
  const c = store.compositionReport
  return c && c.total ? (c.floating_total / c.total) * 100 : 0
})

// Burn-floor health: fixed expenses as a share of income — the "survival
// threshold". Fixed total comes from the composition report, income from the
// income-expense summary (both cover the same window).
const fixedToIncomePct = computed(() => {
  const income = store.incomeExpenseReport?.summary.total_income ?? 0
  const fixed = store.compositionReport?.fixed_total ?? 0
  return income ? (fixed / income) * 100 : 0
})

const budget = computed(() => store.budgetReport)

function usageStatus(rate: number): 'exception' | 'warning' | undefined {
  if (rate > 1) return 'exception'
  if (rate >= 0.9) return 'warning'
  return undefined
}

const cashFlow = computed(() => store.cashFlowReport)

const waterfallItems = computed(() =>
  (store.cashFlowReport?.summary.activities ?? []).map((a) => ({ name: a.label, value: a.net })),
)

function cfTooltip(act: CashFlowActivity): string {
  return act.items
    .map((i) => `${i.label}：${i.amount < 0 ? '−' : '+'}${formatMoney(Math.abs(i.amount))}`)
    .join('<br/>')
}

const insights = computed(() => store.insightsReport)

function fmtDate(d: string): string {
  return d.length === 8 ? `${d.slice(0, 4)}/${d.slice(4, 6)}/${d.slice(6, 8)}` : d
}

function yoyRateText(row: { previous: number; yoy_rate: number }): string {
  if (!row.previous) return '—'
  const pct = row.yoy_rate * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(0)}%`
}

function yoyClass(delta: number): string {
  if (delta > 0) return 'text-secondary' // spending up — worth attention
  if (delta < 0) return 'text-positive' // spending down — good
  return 'text-on-surface-variant'
}

function typeLabel(type: string): string {
  return type.toLowerCase() === 'fixed' ? t('spending.typeFixed') : t('spending.typeFloating')
}

function typeTagType(t: string): 'info' | 'warning' {
  return t.toLowerCase() === 'fixed' ? 'info' : 'warning'
}
</script>
