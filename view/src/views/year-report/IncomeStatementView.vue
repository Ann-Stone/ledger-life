<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('incomeStatement.title')" :subtitle="t('incomeStatement.subtitle', { year: store.selectedYear })">
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
      <el-tab-pane :label="t('incomeStatement.tabMonthly')" name="monthly" />
      <el-tab-pane :label="t('incomeStatement.tabYearly')" name="yearly" />
    </el-tabs>

    <el-skeleton v-if="store.incomeStatementLoading" :rows="6" animated />
    <EmptyState v-else-if="!hasData" :message="t('incomeStatement.empty')" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard
          :label="t('incomeStatement.operatingNet')"
          :amount="summary.operating_net"
          :tone="summary.operating_net < 0 ? 'rose' : 'primary'"
          :tooltip="t('incomeStatement.operatingTooltip')"
        />
        <MetricCard
          :label="t('incomeStatement.investmentNet')"
          :amount="summary.investment_net"
          :tone="summary.investment_net < 0 ? 'rose' : 'primary'"
          :tooltip="t('incomeStatement.investmentTooltip')"
        />
        <MetricCard
          :label="t('incomeStatement.comprehensiveNet')"
          :amount="summary.comprehensive_net"
          :tone="summary.comprehensive_net < 0 ? 'rose' : 'primary'"
          :tooltip="t('incomeStatement.comprehensiveTooltip')"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('incomeStatement.composition')" />
        <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
          <WaterfallChart :items="waterfallItems" :total-label="t('incomeStatement.comprehensiveNet')" height="320px" />
        </div>
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('incomeStatement.byPeriod')" />
        <BarChart :x-data="chart.xData" :series="chart.series" height="360px" />
      </section>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('incomeStatement.detail')" />
        <p class="text-on-surface-variant/70 text-sm -mt-2">
          {{ t('incomeStatement.detailNote') }}
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
import { buildIncomeStatementTree } from './incomeStatementTree'

const store = useYearReportStore()
const { t } = useI18n()

const activeType = ref<'monthly' | 'yearly'>('monthly')

function reload() {
  void store.fetchIncomeStatement(activeType.value, store.selectedYear)
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
  () => !!store.incomeStatementReport && store.incomeStatementReport.points.length > 0,
)

const summary = computed(
  () =>
    store.incomeStatementReport?.summary ?? {
      active_income: 0,
      fixed: 0,
      floating: 0,
      loan_interest: 0,
      operating_net: 0,
      dividend: 0,
      realized: 0,
      unrealized: 0,
      investment_net: 0,
      comprehensive_net: 0,
    },
)

const chart = computed(() => {
  const report = store.incomeStatementReport
  if (!report) return { xData: [], series: [] }
  return {
    xData: report.points.map((p) => p.period),
    series: [
      // 本業淨額 and 投資損益 stack into 綜合損益; the line traces the total.
      { name: t('incomeStatement.operatingNet'), data: report.points.map((p) => p.operating_net), stack: 'pnl' },
      { name: t('incomeStatement.investmentNet'), data: report.points.map((p) => p.investment_net), stack: 'pnl' },
      {
        name: t('incomeStatement.comprehensiveNet'),
        data: report.points.map((p) => p.comprehensive_net),
        type: 'line' as const,
      },
    ],
  }
})

const waterfallItems = computed(() => [
  { name: t('incomeStatement.operatingNet'), value: summary.value.operating_net },
  { name: t('incomeStatement.investmentNet'), value: summary.value.investment_net },
])

const breakdownTree = computed(() => buildIncomeStatementTree(summary.value, t))
</script>
