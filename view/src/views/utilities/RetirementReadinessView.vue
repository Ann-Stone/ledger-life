<template>
  <div class="flex flex-col gap-6">
    <PageHeader :title="t('retirement.title')" :subtitle="t('retirement.subtitle')" />

    <el-skeleton v-if="loading" :rows="8" animated />

    <template v-else-if="data">
      <!-- Parameters -->
      <section
        class="flex flex-col gap-4 rounded-xl border border-outline-variant bg-surface-container p-6"
      >
        <SectionHeader :title="t('retirement.settingsTitle')" />
        <div class="flex flex-wrap items-end gap-8">
          <div class="flex flex-col gap-1">
            <label class="text-on-surface-variant text-xs">{{ t('retirement.withdrawalRate') }}</label>
            <div class="flex items-center gap-2">
              <el-input-number v-model="ratePct" :min="1" :max="10" :step="0.1" :precision="1" />
              <span class="text-on-surface-variant">%</span>
            </div>
            <p class="text-on-surface-variant text-xs">{{ t('retirement.withdrawalRateHint') }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-on-surface-variant text-xs">{{ t('retirement.expenseOverride') }}</label>
            <el-input-number
              v-model="overrideInput"
              :min="0"
              :step="10000"
              :precision="0"
              controls-position="right"
              class="w-44"
            />
            <p class="text-on-surface-variant text-xs">{{ t('retirement.expenseOverrideHint') }}</p>
          </div>
          <div class="flex flex-col gap-1">
            <label class="text-on-surface-variant text-xs">{{ t('retirement.excludeSelfOccupied') }}</label>
            <el-switch v-model="excludeSelfOccupied" />
            <p class="text-on-surface-variant text-xs">{{ t('retirement.excludeSelfOccupiedHint') }}</p>
          </div>
          <el-button type="primary" :loading="saving" @click="save">
            {{ t('retirement.save') }}
          </el-button>
        </div>
      </section>

      <!-- Readiness -->
      <section
        class="flex flex-col gap-4 rounded-xl border border-outline-variant bg-surface-container p-6"
      >
        <SectionHeader :title="t('retirement.readinessTitle')" />
        <div class="flex flex-wrap items-center gap-10">
          <el-progress
            type="dashboard"
            :percentage="readinessClamped"
            :color="gaugeColor"
            :width="170"
          >
            <template #default>
              <div class="flex flex-col items-center">
                <span class="text-2xl font-semibold">{{ pct(data.readiness_pct) }}</span>
                <span class="text-on-surface-variant text-xs">{{ t('retirement.readiness') }}</span>
              </div>
            </template>
          </el-progress>
          <div class="grid grid-cols-2 gap-x-12 gap-y-4">
            <div class="flex flex-col gap-1">
              <span class="text-on-surface-variant text-xs">{{ t('retirement.targetPortfolio') }}</span>
              <MoneyDisplay :amount="data.target_portfolio" size="lg" />
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-on-surface-variant text-xs">{{ t('retirement.netWorth') }}</span>
              <MoneyDisplay :amount="data.net_worth" size="lg" />
              <span
                v-if="data.self_occupied_estate_value > 0"
                class="text-on-surface-variant text-xs"
              >
                {{ t('retirement.selfOccupiedExcluded', { amount: money(data.self_occupied_estate_value) }) }}
              </span>
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-on-surface-variant text-xs">
                {{ data.gap > 0 ? t('retirement.gap') : t('retirement.surplus') }}
              </span>
              <MoneyDisplay :amount="Math.abs(data.gap)" :positive="data.gap <= 0" size="lg" />
            </div>
            <div class="flex flex-col gap-1">
              <span class="text-on-surface-variant text-xs">{{ t('retirement.annualBase') }}</span>
              <MoneyDisplay :amount="data.annual_expense_base" size="lg" />
            </div>
          </div>
        </div>
        <p class="text-on-surface-variant text-xs">
          {{ data.expense_base_source === 'override' ? t('retirement.basisOverride') : t('retirement.basisComputed') }}
        </p>
      </section>

      <!-- Cash-flow health (during the loan years) -->
      <section class="flex flex-col gap-4">
        <SectionHeader :title="t('retirement.cashFlowTitle')" />
        <div class="grid grid-cols-1 gap-4 md:grid-cols-3">
          <div class="flex flex-col gap-1 rounded-xl border border-outline-variant bg-surface-container p-5">
            <span class="text-on-surface-variant text-xs">{{ t('retirement.debtServiceRatio') }}</span>
            <span class="text-2xl font-semibold tabular-nums" :class="debtToneClass">{{ pct(data.debt_service_ratio) }}</span>
          </div>
          <div class="flex flex-col gap-1 rounded-xl border border-outline-variant bg-surface-container p-5">
            <span class="text-on-surface-variant text-xs">{{ t('retirement.monthlyIncome') }}</span>
            <MoneyDisplay :amount="data.monthly_income" size="lg" />
          </div>
          <div class="flex flex-col gap-1 rounded-xl border border-outline-variant bg-surface-container p-5">
            <span class="text-on-surface-variant text-xs">{{ t('retirement.monthlyLoanPayment') }}</span>
            <MoneyDisplay :amount="data.monthly_loan_payment" :positive="false" size="lg" />
          </div>
        </div>

        <el-table v-if="data.loans.length" :data="data.loans" row-key="loan_id" border>
          <el-table-column prop="loan_name" :label="t('retirement.colLoan')" min-width="140" />
          <el-table-column :label="t('retirement.colRemaining')" width="160" align="right">
            <template #default="{ row }"><MoneyDisplay :amount="row.remaining_balance" /></template>
          </el-table-column>
          <el-table-column :label="t('retirement.colMonthly')" width="150" align="right">
            <template #default="{ row }"><MoneyDisplay :amount="row.monthly_payment" /></template>
          </el-table-column>
          <el-table-column :label="t('retirement.colPayoff')" width="120" align="center">
            <template #default="{ row }">{{ fmtMonth(row.payoff_month) }}</template>
          </el-table-column>
          <el-table-column :label="t('retirement.colYearsLeft')" width="110" align="right">
            <template #default="{ row }">
              {{ row.years_left == null ? t('retirement.unknown') : `${row.years_left} ${t('retirement.yearsUnit')}` }}
            </template>
          </el-table-column>
        </el-table>
      </section>
    </template>

    <EmptyState v-else :message="t('retirement.empty')" />
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import {
  getRetirementReadiness,
  getRetirementSettings,
  updateRetirementSettings,
} from '@/api/dashboard'
import { useMoney } from '@/composables/useMoney'
import type { RetirementReadiness } from '@/types/models'

const { t } = useI18n()
const { format: formatMoney } = useMoney()

const data = ref<RetirementReadiness | null>(null)
const loading = ref(true)
const saving = ref(false)
const ratePct = ref(4)
const overrideInput = ref(0)
const excludeSelfOccupied = ref(true)

function pct(v: number): string {
  return `${(v * 100).toFixed(1)}%`
}

function money(v: number): string {
  return formatMoney(v, { maximumFractionDigits: 0 })
}

function fmtMonth(m: string | null): string {
  if (!m || m.length !== 6) return t('retirement.unknown')
  return `${m.slice(0, 4)}/${m.slice(4, 6)}`
}

const readinessClamped = computed(() =>
  Math.max(0, Math.min(100, Math.round((data.value?.readiness_pct ?? 0) * 100))),
)

const gaugeColor = computed(() => {
  const r = data.value?.readiness_pct ?? 0
  if (r >= 1) return '#16a34a'
  if (r >= 0.5) return '#d97706'
  return '#dc2626'
})

const debtToneClass = computed(() => {
  const r = data.value?.debt_service_ratio ?? 0
  if (r >= 0.4) return 'text-negative'
  if (r >= 0.3) return 'text-amber-600'
  return 'text-on-surface'
})

async function load() {
  loading.value = true
  try {
    const [readiness, settings] = await Promise.all([
      getRetirementReadiness(),
      getRetirementSettings(),
    ])
    data.value = readiness
    ratePct.value = Math.round(settings.withdrawal_rate * 1000) / 10
    overrideInput.value = settings.annual_expense_override ?? 0
    excludeSelfOccupied.value = settings.exclude_self_occupied_estate
  } finally {
    loading.value = false
  }
}

async function save() {
  saving.value = true
  try {
    await updateRetirementSettings({
      withdrawal_rate: ratePct.value / 100,
      annual_expense_override: overrideInput.value > 0 ? overrideInput.value : null,
      exclude_self_occupied_estate: excludeSelfOccupied.value,
    })
    ElMessage.success(t('retirement.saved'))
    await load()
  } finally {
    saving.value = false
  }
}

onMounted(load)
</script>
