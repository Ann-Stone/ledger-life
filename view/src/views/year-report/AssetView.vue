<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('asset.title')" :subtitle="t('common.yearLabel', { year: store.selectedYear })">
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

    <el-skeleton v-if="store.assetsLoading" :rows="6" animated />
    <EmptyState
      v-else-if="!store.assetsReport || store.assetsReport.items.length === 0"
      :message="t('asset.empty')"
    />
    <template v-else>
      <MetricCard :label="t('asset.totalAssets')" :amount="store.assetsReport.total" />

      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('asset.composition')" />
          <DonutChart :data="donutData" :center-text="centerText" height="360px" />
        </section>

        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('asset.detail')" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="store.assetsReport.items" stripe border style="width: 100%">
              <el-table-column prop="type" :label="t('common.category')" min-width="140">
                <template #default="{ row }">
                  <span>{{ assetTypeLabel(row.type) }}</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.amount')" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('asset.share')" width="120" align="right">
                <template #default="{ row }">
                  <SharePercent :value="row.share" class="text-on-surface" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </section>
      </div>

      <section v-if="hasStockAllocation" class="flex flex-col gap-4">
        <SectionHeader :title="t('asset.stockAllocation')" />
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <DonutChart :data="stockDonutData" :center-text="stockCenterText" height="320px" />
          <div class="rounded-xl border border-outline-variant bg-surface-container p-4">
            <el-table :data="store.stockAllocation!.items" stripe border style="width: 100%">
              <el-table-column prop="category_name" :label="t('asset.category')" min-width="140" />
              <el-table-column :label="t('common.amount')" width="180" align="right">
                <template #default="{ row }">
                  <MoneyDisplay :amount="row.amount" :positive="true" size="sm" />
                </template>
              </el-table-column>
              <el-table-column :label="t('asset.share')" width="120" align="right">
                <template #default="{ row }">
                  <SharePercent :value="row.share" class="text-on-surface" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </div>
      </section>
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
import DonutChart from '@/components/charts/DonutChart.vue'
import { useYearReportStore } from '@/stores/yearReport'
import { useMoney } from '@/composables/useMoney'
import { useYearDatePicker } from '@/composables/useYearDatePicker'

const store = useYearReportStore()
const { t } = useI18n()
const { format: formatMoney } = useMoney()

const TYPE_LABEL: Record<string, string> = {
  accounts: 'asset.typeAccounts',
  stocks: 'asset.typeStocks',
  estates: 'asset.typeEstates',
  insurances: 'asset.typeInsurances',
  other_assets: 'asset.typeOtherAssets',
}

function assetTypeLabel(type: string): string {
  const key = TYPE_LABEL[type]
  return key ? t(key) : type
}

const { selectedYearDate } = useYearDatePicker({
  current: () => store.selectedYear,
  onChange: (year) => void store.fetchAssetsReport(year),
})

onMounted(() => {
  void store.fetchAssetsReport(store.selectedYear)
  void store.fetchStockAllocation()
})

const donutData = computed(() =>
  store.assetsReport
    ? store.assetsReport.items.map((i) => ({
        name: assetTypeLabel(i.type),
        value: i.amount,
      }))
    : [],
)

const centerText = computed(() => {
  if (!store.assetsReport) return ''
  const total = formatMoney(store.assetsReport.total, { maximumFractionDigits: 0 })
  return t('asset.donutCenter', { total })
})

const hasStockAllocation = computed(
  () => !!store.stockAllocation && store.stockAllocation.items.length > 0,
)

const stockDonutData = computed(() =>
  store.stockAllocation
    ? store.stockAllocation.items.map((i) => ({ name: i.category_name, value: i.amount }))
    : [],
)

const stockCenterText = computed(() => {
  if (!store.stockAllocation) return ''
  const total = formatMoney(store.stockAllocation.total, { maximumFractionDigits: 0 })
  return t('asset.stockDonutCenter', { total })
})
</script>
