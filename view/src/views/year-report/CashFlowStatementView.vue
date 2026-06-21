<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('cashFlowStatement.title')" :subtitle="t('cashFlowStatement.subtitle', { year: store.selectedYear })">
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

    <el-skeleton v-if="store.cashFlowLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" :message="t('cashFlowStatement.empty')" />
    <template v-else>
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <MetricCard
          :label="t('cashFlowStatement.operatingNet')"
          :amount="nets.operating"
          :tone="nets.operating < 0 ? 'rose' : 'primary'"
          :tooltip="t('cashFlowStatement.operatingTooltip')"
        />
        <MetricCard
          :label="t('cashFlowStatement.investingNet')"
          :amount="nets.investing"
          :tone="nets.investing < 0 ? 'rose' : 'primary'"
          :tooltip="t('cashFlowStatement.investingTooltip')"
        />
        <MetricCard
          :label="t('cashFlowStatement.financingNet')"
          :amount="nets.financing"
          :tone="nets.financing < 0 ? 'rose' : 'primary'"
          :tooltip="t('cashFlowStatement.financingTooltip')"
        />
        <MetricCard
          :label="t('cashFlowStatement.netChange')"
          :amount="summary.net_change"
          :tone="summary.net_change < 0 ? 'rose' : 'primary'"
          :tooltip="t('cashFlowStatement.netChangeTooltip')"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('cashFlowStatement.composition')" />
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <WaterfallChart :items="waterfallItems" :total-label="t('cashFlowStatement.netChange')" height="320px" />
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('cashFlowStatement.byPeriod')" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('cashFlowStatement.detail')" />
        <p class="text-on-surface-variant/70 text-sm -mt-2">
          {{ t('cashFlowStatement.detailNote') }}
        </p>
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <el-table
            :data="breakdownTree"
            row-key="key"
            :tree-props="{ children: 'children' }"
            default-expand-all
            border
            style="width: 100%"
          >
            <el-table-column prop="label" :label="t('common.item')" min-width="220" />
            <el-table-column :label="t('common.amount')" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay
                  :amount="row.amount"
                  currency="TWD"
                  :positive="row.amount >= 0"
                  size="sm"
                />
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
import BarChart from '@/components/charts/BarChart.vue'
import WaterfallChart from '@/components/charts/WaterfallChart.vue'
import { useYearReportStore } from '@/stores/yearReport'
import { useYearDatePicker } from '@/composables/useYearDatePicker'
import { buildCashFlowTree } from './cashFlowStatementTree'

const store = useYearReportStore()
const { t } = useI18n()

const activeType = ref<'monthly' | 'yearly'>('monthly')

function reload() {
  void store.fetchCashFlow(activeType.value, store.selectedYear)
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
  () => !!store.cashFlowReport && store.cashFlowReport.points.length > 0,
)

const summary = computed(
  () => store.cashFlowReport?.summary ?? { activities: [], net_change: 0 },
)

// Signed net per activity, keyed by 'operating' | 'investing' | 'financing'.
const nets = computed(() => {
  const m = { operating: 0, investing: 0, financing: 0 } as Record<string, number>
  for (const a of summary.value.activities) m[a.key] = a.net
  return m
})

const chart = computed(() => {
  const report = store.cashFlowReport
  if (!report) return { xData: [] as string[], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      // 生活 / 投資 / 債務 stack into 現金淨變動; the line traces the total.
      { name: t('cashFlowStatement.seriesOperating'), data: report.points.map((p) => p.operating), stack: 'cf' },
      { name: t('cashFlowStatement.seriesInvesting'), data: report.points.map((p) => p.investing), stack: 'cf' },
      { name: t('cashFlowStatement.seriesFinancing'), data: report.points.map((p) => p.financing), stack: 'cf' },
      {
        name: t('cashFlowStatement.netChange'),
        data: report.points.map((p) => p.net_change),
        type: 'line' as const,
      },
    ],
  }
})

const waterfallItems = computed(() => [
  { name: t('cashFlowStatement.seriesOperating'), value: nets.value.operating },
  { name: t('cashFlowStatement.seriesInvesting'), value: nets.value.investing },
  { name: t('cashFlowStatement.seriesFinancing'), value: nets.value.financing },
])

const breakdownTree = computed(() => buildCashFlowTree(summary.value, t))
</script>
