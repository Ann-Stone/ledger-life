<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('balanceSheet.title')" :subtitle="t('common.yearLabel', { year: store.selectedYear })">
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

    <el-skeleton v-if="store.balanceLoading" :rows="6" animated />
    <EmptyState v-else-if="!store.balanceReport" :message="t('balanceSheet.empty')" />
    <template v-else>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <MetricCard :label="t('balanceSheet.totalAssets')" :amount="totalAssets" />
        <MetricCard :label="t('balanceSheet.totalLiabilities')" :amount="totalLiabilities" tone="rose" />
        <MetricCard
          :label="t('balanceSheet.netAssets')"
          :amount="store.balanceReport.net_worth"
          :tone="store.balanceReport.net_worth < 0 ? 'rose' : 'primary'"
        />
      </div>

      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('balanceSheet.categoryOverview')" />
        <BarChart :x-data="categoryChart.xData" :series="categoryChart.series" height="320px" />
      </section>

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('balanceSheet.assetDetail')" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table
              :data="assetTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" :label="t('common.item')" min-width="200" />
              <el-table-column :label="t('common.amount')" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" currency="TWD" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('balanceSheet.originalCurrency')" width="140" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    v-if="row.originalCurrency && row.originalCurrency !== 'TWD'"
                    :amount="row.originalAmount"
                    :currency="row.originalCurrency"
                    size="sm"
                  />
                  <span v-else class="text-on-surface-variant/40">—</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('balanceSheet.share')" width="84" align="right">
                <template #default="{ row }">
                  <SharePercent :value="row.share" class="text-sm text-on-surface-variant" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>

        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('balanceSheet.liabilityDetail')" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table
              :data="liabilityTree"
              row-key="key"
              :tree-props="{ children: 'children' }"
              border
              style="width: 100%"
            >
              <el-table-column prop="label" :label="t('common.item')" min-width="200" />
              <el-table-column :label="t('common.amount')" width="160" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    :amount="Math.abs(row.amount)"
                    currency="TWD"
                    :positive="false"
                    size="sm"
                  />
                </template>
              </el-table-column>
              <el-table-column :label="t('balanceSheet.originalCurrency')" width="140" align="right">
                <template #default="{ row }">
                  <MoneyDisplay
                    v-if="row.originalCurrency && row.originalCurrency !== 'TWD'"
                    :amount="Math.abs(row.originalAmount)"
                    :currency="row.originalCurrency"
                    :positive="false"
                    size="sm"
                  />
                  <span v-else class="text-on-surface-variant/40">—</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('balanceSheet.share')" width="84" align="right">
                <template #default="{ row }">
                  <SharePercent :value="row.share" class="text-sm text-on-surface-variant" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import SharePercent from '@/components/ui/SharePercent.vue'
import BarChart from '@/components/charts/BarChart.vue'
import { useYearReportStore } from '@/stores/yearReport'
import { useYearDatePicker } from '@/composables/useYearDatePicker'
import {
  buildAssetTree,
  buildLiabilityTree,
  totalAssets as sumAssets,
  totalLiabilities as sumLiabilities,
} from './balanceTree'

const store = useYearReportStore()
const { t } = useI18n()

const { selectedYearDate } = useYearDatePicker({
  current: () => store.selectedYear,
  onChange: (year) => void store.fetchBalanceReport(year),
})

onMounted(() => {
  void store.fetchBalanceReport(store.selectedYear)
})

const assetTree = computed(() =>
  store.balanceReport ? buildAssetTree(store.balanceReport) : [],
)

const liabilityTree = computed(() =>
  store.balanceReport ? buildLiabilityTree(store.balanceReport) : [],
)

const totalAssets = computed(() =>
  store.balanceReport ? sumAssets(store.balanceReport) : 0,
)

const totalLiabilities = computed(() =>
  store.balanceReport ? sumLiabilities(store.balanceReport) : 0,
)

const categoryChart = computed(() => {
  const xData = [
    ...assetTree.value.map((n) => n.label),
    ...liabilityTree.value.map((n) => n.label),
  ]
  const data = [
    ...assetTree.value.map((n) => n.amount),
    ...liabilityTree.value.map((n) => Math.abs(n.amount)),
  ]
  return { xData, series: [{ name: t('common.amount'), data }] }
})
</script>
