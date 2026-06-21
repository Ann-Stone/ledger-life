<template>
  <div class="flex flex-col gap-6">
    <PageHeader :title="t('settingBudget.title')" :subtitle="t('settingBudget.subtitle')">
      <template #actions>
        <el-select
          v-model="selectedYear"
          :placeholder="t('settingBudget.pickYear')"
          style="width: 140px"
          @change="reload"
        >
          <el-option
            v-for="y in store.budgetYears"
            :key="y"
            :label="y"
            :value="y"
          />
        </el-select>
        <el-button :loading="suggesting" @click="handleSuggest">
          {{ t('settingBudget.suggest') }}
        </el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ t('common.save') }}
        </el-button>
      </template>
    </PageHeader>

    <el-alert
      v-if="previewDirty"
      type="info"
      :closable="false"
      show-icon
      :title="t('settingBudget.previewDirty')"
    />

    <DataListCard :title="t('settingBudget.budgetCardTitle', { year: selectedYear })">
      <div class="p-4">
        <el-table
          :data="ordinaryBudgets"
          v-loading="store.budgetsLoading"
          border
          stripe
          :empty-text="t('settingBudget.empty')"
          max-height="640"
        >
          <el-table-column
            prop="category_name"
            :label="t('common.category')"
            width="180"
            fixed="left"
          >
            <template #default="{ row }">
              <div class="flex flex-col">
                <span class="font-semibold text-on-surface">{{ row.category_name }}</span>
                <span class="text-xs text-on-surface-muted">{{ row.category_code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column
            v-for="m in MONTH_KEYS"
            :key="m.key"
            :label="t('settingBudget.monthLabel', { n: m.month })"
            min-width="120"
          >
            <template #default="{ row }">
              <el-input-number
                v-model="row[m.key]"
                :min="0"
                :step="1000"
                :precision="0"
                :controls="false"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
        </el-table>
      </div>
    </DataListCard>

    <DataListCard
      v-if="eventBudgets.length"
      :title="t('settingBudget.eventCardTitle', { year: selectedYear })"
    >
      <div class="p-4">
        <el-table :data="eventBudgets" border stripe max-height="400">
          <el-table-column prop="category_name" :label="t('common.category')" min-width="180">
            <template #default="{ row }">
              <div class="flex flex-col">
                <span class="font-semibold text-on-surface">{{ row.category_name }}</span>
                <span class="text-xs text-on-surface-muted">{{ row.category_code }}</span>
              </div>
            </template>
          </el-table-column>
          <el-table-column :label="t('settingBudget.annualAmount')" min-width="220">
            <template #default="{ row }">
              <el-input-number
                v-model="row.annual_amount"
                :min="0"
                :step="1000"
                :precision="0"
                :controls="false"
                size="small"
                style="width: 100%"
              />
            </template>
          </el-table-column>
        </el-table>
        <p class="mt-2 text-xs text-on-surface-muted">
          {{ t('settingBudget.eventHint') }}
        </p>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { ElMessage } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import { useSettingStore } from '@/stores/setting'
import { applyBudget, getCodes, suggestBudget } from '@/api/setting'

const MONTH_KEYS = [
  { key: 'expected01', month: 1 },
  { key: 'expected02', month: 2 },
  { key: 'expected03', month: 3 },
  { key: 'expected04', month: 4 },
  { key: 'expected05', month: 5 },
  { key: 'expected06', month: 6 },
  { key: 'expected07', month: 7 },
  { key: 'expected08', month: 8 },
  { key: 'expected09', month: 9 },
  { key: 'expected10', month: 10 },
  { key: 'expected11', month: 11 },
  { key: 'expected12', month: 12 },
] as const

const { t } = useI18n()
const store = useSettingStore()
const selectedYear = ref<string>(String(new Date().getFullYear()))
const saving = ref(false)
const suggesting = ref(false)
const previewDirty = ref(false)
const eventCodeIds = ref<Set<string>>(new Set())

const ordinaryBudgets = computed(() =>
  store.budgets.filter((b) => !eventCodeIds.value.has(b.category_code)),
)
const eventBudgets = computed(() =>
  store.budgets.filter((b) => eventCodeIds.value.has(b.category_code)),
)

onMounted(async () => {
  await store.fetchBudgetYears()
  const first = store.budgetYears[0]
  if (first && !store.budgetYears.includes(selectedYear.value)) {
    selectedYear.value = first
  }
  await reload()
})

async function reload() {
  previewDirty.value = false
  const [, codes] = await Promise.all([
    store.fetchBudgets(Number(selectedYear.value)),
    getCodes(),
  ])
  eventCodeIds.value = new Set(
    codes.filter((c) => c.is_annual_event).map((c) => c.code_id),
  )
}

async function handleSuggest() {
  suggesting.value = true
  try {
    store.budgets = await suggestBudget(Number(selectedYear.value))
    previewDirty.value = true
    ElMessage.success(t('settingBudget.suggestApplied'))
  } finally {
    suggesting.value = false
  }
}

async function handleSave() {
  saving.value = true
  try {
    await applyBudget(Number(selectedYear.value), store.budgets)
    ElMessage.success(t('settingBudget.saveSuccess'))
    await reload()
  } finally {
    saving.value = false
  }
}
</script>
