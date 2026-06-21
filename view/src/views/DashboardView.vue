<template>
  <div class="h-auto md:h-full flex flex-col gap-6 md:gap-4 overflow-y-auto md:overflow-hidden">
    <section
      class="flex flex-wrap items-center justify-between gap-4 pb-4 border-b border-outline-variant shrink-0"
    >
      <el-radio-group v-model="viewMode" size="default">
        <el-radio-button :label="t('dashboard.viewMonth')" value="month" />
        <el-radio-button :label="t('dashboard.viewYear')" value="year" />
      </el-radio-group>

      <el-date-picker
        v-if="viewMode === 'month'"
        v-model="monthPick"
        type="month"
        format="YYYY/MM"
        value-format="YYYYMM"
        :clearable="false"
        size="default"
      />
      <el-date-picker
        v-else
        v-model="yearPick"
        type="year"
        format="YYYY"
        value-format="YYYY"
        :clearable="false"
        size="default"
      />
    </section>

    <section v-if="(store.uncategorized?.total ?? 0) > 0" class="shrink-0">
      <el-alert type="warning" :closable="false" show-icon>
        <template #title>
          {{ t('dashboard.uncategorizedTitle', { total: store.uncategorized?.total ?? 0 }) }}
        </template>
        <div class="flex flex-wrap items-center gap-2 pt-1">
          <span class="text-xs">{{ t('dashboard.uncategorizedHint') }}</span>
          <el-tag
            v-for="m in uncategorizedMonths"
            :key="m.vesting_month"
            type="warning"
            size="small"
            class="cursor-pointer"
            @click="goCleanUpMonth(m.vesting_month)"
          >
            {{ m.vesting_month.slice(0, 4) }}/{{ m.vesting_month.slice(4) }} · {{ m.count }}
          </el-tag>
          <span v-if="uncategorizedMoreCount > 0" class="text-xs">
            {{ t('dashboard.uncategorizedMore', { count: uncategorizedMoreCount }) }}
          </span>
        </div>
      </el-alert>
    </section>

    <section class="grid grid-cols-1 md:grid-cols-3 gap-4 md:gap-6 shrink-0">
      <el-skeleton
        v-if="store.summariesLoading.asset_debt_trend"
        :rows="3"
        animated
      />
      <MetricCard
        v-else-if="store.viewMode === 'month'"
        :label="t('dashboard.netWorth')"
        :amount="latestNetWorth"
        :points="store.summaries.asset_debt_trend?.points ?? []"
      />
      <MetricCard
        v-else
        :label="t('dashboard.netWorth')"
        :amount="latestNetWorth"
        :delta-percent="netWorthYoYDelta"
        :delta-label="t('dashboard.vsLastYear')"
      />

      <el-skeleton
        v-if="store.summariesLoading.freedom_ratio"
        :rows="3"
        animated
      />
      <MetricCard
        v-else-if="store.viewMode === 'month'"
        :label="t('dashboard.freedomRatio')"
        format="percent"
        :amount="freedomPercentValue"
        :points="freedomRatioPercentPoints"
        :tooltip="freedomRatioTooltip"
      />
      <MetricCard
        v-else
        :label="t('dashboard.freedomRatio')"
        format="percent"
        :amount="freedomPercentValue"
        :delta-percent="freedomYoYDelta"
        :delta-label="t('dashboard.vsLastYear')"
        :tooltip="freedomRatioTooltip"
      />

      <el-skeleton
        v-if="store.summariesLoading.work_freedom_ratio"
        :rows="3"
        animated
      />
      <MetricCard
        v-else-if="store.viewMode === 'month'"
        :label="t('dashboard.workFreedomRatio')"
        format="percent"
        :amount="workFreedomPercentValue"
        :points="workFreedomRatioPercentPoints"
        :tooltip="workFreedomRatioTooltip"
      />
      <MetricCard
        v-else
        :label="t('dashboard.workFreedomRatio')"
        format="percent"
        :amount="workFreedomPercentValue"
        :delta-percent="workFreedomYoYDelta"
        :delta-label="t('dashboard.vsLastYear')"
        :tooltip="workFreedomRatioTooltip"
      />
    </section>

    <section class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6 md:grow-[3] md:basis-0 md:min-h-0">
      <div
        class="lg:col-span-2 rounded-xl bg-surface-container border border-outline-variant p-4 flex flex-col md:min-h-0"
      >
        <el-skeleton
          v-if="store.summariesLoading.asset_debt_trend"
          :rows="6"
          animated
          class="flex-1"
        />
        <AssetTrendChart v-else :points="assetTrendPoints" :height="appStore.isMobile ? '300px' : '100%'" class="flex-1 min-h-0" />
      </div>
      <div class="lg:col-span-1 flex flex-col gap-4 lg:gap-6 md:min-h-0 md:h-full">
        <el-skeleton v-if="store.budgetLoading" :rows="3" animated class="shrink-0" />
        <MetricCard
          v-else
          :label="budgetCardLabel"
          format="percent"
          :amount="budgetUsagePct"
          :delta-label="budgetUsageDeltaLabel"
          class="shrink-0"
        />
        <MetricCard
          v-if="!store.budgetLoading && hasEventBudget"
          :label="t('dashboard.eventEnvelope')"
          format="percent"
          :amount="eventUsagePct"
          :delta-label="eventUsageDeltaLabel"
          class="shrink-0"
        />
        <el-skeleton v-if="store.giftsLoading" :rows="3" animated class="flex-1" />
        <EmptyState
          v-else-if="store.gifts.length === 0"
          :message="t('dashboard.noGifts', { year: store.anchorYear })"
          class="flex-1 min-h-0"
        />
        <DataListCard v-else :title="t('dashboard.giftsTitle', { year: store.anchorYear })" class="md:flex-1 md:min-h-0">
          <div
            v-for="(g, idx) in store.gifts"
            :key="`${g.owner}-${idx}`"
            class="flex items-center justify-between px-5 py-2.5"
          >
            <p class="text-on-surface text-sm font-semibold">{{ g.owner }}</p>
            <div class="flex items-center gap-3">
              <MoneyDisplay :amount="g.amount" size="sm" />
              <span
                class="tabular-nums text-xs font-bold px-2 py-0.5 rounded-full"
                :class="giftRateClass(g.rate)"
              >
                {{ g.rate.toFixed(1) }}%
              </span>
            </div>
          </div>
        </DataListCard>
      </div>
    </section>

    <section class="flex flex-col gap-3 md:grow-[2] md:basis-0 md:min-h-0">
      <SectionHeader :title="t('dashboard.trackingTitle')" class="shrink-0">
        <template #actions>
          <div class="flex items-center gap-2">
            <el-button
              :disabled="archivedTargets.length === 0"
              :icon="FolderOpened"
              size="small"
              @click="archiveDialogVisible = true"
            >
              {{ t('dashboard.archivedCount', { count: archivedTargets.length }) }}
            </el-button>
            <el-button type="primary" :icon="Plus" size="small" @click="openTargetCreate">
              {{ t('common.add') }}
            </el-button>
          </div>
        </template>
      </SectionHeader>
      <el-skeleton v-if="store.targetsLoading" :rows="3" animated class="md:flex-1" />
      <EmptyState v-else-if="activeTargets.length === 0" :message="t('dashboard.noTracking')" class="md:flex-1 md:min-h-0" />
      <DataListCard v-else class="md:flex-1 md:min-h-0">
        <div
          v-for="target in activeTargets"
          :key="target.distinct_number"
          class="flex items-center justify-between px-5 py-3"
        >
          <div class="flex flex-col gap-1 min-w-0 flex-1 pr-4">
            <p class="text-on-surface text-sm font-semibold">
              {{ target.setting_value }}
            </p>
            <p class="text-on-surface-variant text-xs">
              {{ t('dashboard.targetMeta', { year: target.target_year, num: target.distinct_number }) }}
            </p>
          </div>
          <div class="flex items-center gap-2">
            <el-button
              :icon="Check"
              size="small"
              class="btn-complete"
              :title="t('dashboard.markDone')"
              @click="markTargetDone(target)"
            />
            <el-button :icon="Edit" size="small" text @click="openTargetEdit(target)" />
            <el-popconfirm
              :title="t('common.confirmDelete')"
              :confirm-button-text="t('common.delete')"
              :cancel-button-text="t('common.cancel')"
              @confirm="handleDeleteTarget(target.distinct_number)"
            >
              <template #reference>
                <el-button :icon="Delete" size="small" text type="danger" />
              </template>
            </el-popconfirm>
          </div>
        </div>
      </DataListCard>

      <el-dialog
        v-model="archiveDialogVisible"
        :title="t('dashboard.archivedTitle')"
        width="560"
      >
        <el-empty
          v-if="archivedTargets.length === 0"
          :description="t('dashboard.noArchived')"
        />
        <ul v-else class="flex flex-col divide-y divide-outline-variant/30 rounded-lg bg-surface-container-low pl-0 list-none">
          <li
            v-for="target in archivedTargets"
            :key="target.distinct_number"
            class="flex items-center justify-between px-4 py-3"
          >
            <div class="flex flex-col gap-1 min-w-0 flex-1 pr-4">
              <p class="text-on-surface text-sm font-semibold truncate">
                {{ target.setting_value }}
              </p>
              <p class="text-on-surface-variant text-xs truncate">
                {{ t('dashboard.targetMeta', { year: target.target_year, num: target.distinct_number }) }}
              </p>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <el-button
                :icon="RefreshLeft"
                size="small"
                text
                :title="t('dashboard.restoreActive')"
                @click="markTargetUndone(target)"
              />
              <el-popconfirm
                :title="t('common.confirmDelete')"
                :confirm-button-text="t('common.delete')"
                :cancel-button-text="t('common.cancel')"
                @confirm="handleDeleteTarget(target.distinct_number)"
              >
                <template #reference>
                  <el-button :icon="Delete" size="small" text type="danger" />
                </template>
              </el-popconfirm>
            </div>
          </li>
        </ul>
      </el-dialog>

      <FormDialog
        v-model="targetDialogVisible"
        :title="editingTarget ? t('dashboard.editTarget') : t('dashboard.addTarget')"
        :loading="targetSubmitting"
        @submit="submitTarget"
      >
        <el-form ref="targetFormRef" :model="targetForm" :rules="targetRules" label-width="100px">
          <el-form-item v-if="editingTarget" :label="t('dashboard.fieldNumber')">
            <span class="text-on-surface-variant text-sm">{{ editingTarget.distinct_number }}</span>
          </el-form-item>
          <el-form-item :label="t('dashboard.fieldYear')" prop="target_year">
            <el-input v-model="targetForm.target_year" placeholder="YYYY" maxlength="4" />
          </el-form-item>
          <el-form-item :label="t('dashboard.fieldContent')" prop="setting_value">
            <el-input v-model="targetForm.setting_value" maxlength="45" show-word-limit :placeholder="t('dashboard.contentPlaceholder')" />
          </el-form-item>
          <el-form-item :label="t('dashboard.fieldStatus')">
            <el-switch v-model="targetForm.is_done" active-value="Y" inactive-value="N" />
          </el-form-item>
        </el-form>
      </FormDialog>
    </section>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import dayjs from 'dayjs'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus, Edit, Delete, Check, FolderOpened, RefreshLeft } from '@element-plus/icons-vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import { useMoney } from '@/composables/useMoney'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import AssetTrendChart from '@/components/charts/AssetTrendChart.vue'
import { useDashboardStore, type ViewMode } from '@/stores/dashboard'
import { useAppStore } from '@/stores/app'
import { createTarget, updateTarget, deleteTarget } from '@/api/dashboard'
import type { TargetSetting } from '@/types/models'

const store = useDashboardStore()
const appStore = useAppStore()
const router = useRouter()
const { t } = useI18n()

// Uncategorized-journal cleanup banner ----------------------------------------
// Show the newest months first; cap the chip row so years of backlog don't
// flood the dashboard.
const UNCATEGORIZED_CHIP_LIMIT = 12

const uncategorizedMonths = computed(
  () => store.uncategorized?.months.slice(0, UNCATEGORIZED_CHIP_LIMIT) ?? [],
)
const uncategorizedMoreCount = computed(() =>
  Math.max((store.uncategorized?.months.length ?? 0) - UNCATEGORIZED_CHIP_LIMIT, 0),
)

function goCleanUpMonth(month: string) {
  router.push({
    path: '/monthly-report/cash-flow',
    query: { month, uncategorized: '1' },
  })
}

// View-mode + anchor controls -------------------------------------------------
// Local refs bound to the radio/picker. Whenever the user changes a control, we
// push the new state into the store and refetch view-dependent data.
const viewMode = ref<ViewMode>(store.viewMode)
const monthPick = ref<string>(
  store.viewMode === 'month' ? store.anchor : dayjs().format('YYYYMM'),
)
const yearPick = ref<string>(
  store.viewMode === 'year' ? store.anchor : dayjs().format('YYYY'),
)

watch(viewMode, (next) => {
  const nextAnchor = next === 'month' ? monthPick.value : yearPick.value
  store.setView(next, nextAnchor)
  store.refetchAllForView()
})

watch(monthPick, (next) => {
  if (viewMode.value !== 'month') return
  store.setView('month', next)
  store.refetchAllForView()
})

watch(yearPick, (next) => {
  if (viewMode.value !== 'year') return
  store.setView('year', next)
  store.refetchAllForView()
})

// Asset trend ----------------------------------------------------------------
// In year view we want only year-end (Dec) snapshots so the 10-year chart has
// 10 points rather than 120. The anchor year contributes its anchor month (it
// hasn't reached December yet for the current year, so we use the latest
// available point for that year).
const assetTrendPoints = computed(() => {
  const pts = store.summaries.asset_debt_trend?.points ?? []
  if (store.viewMode === 'month') return pts
  const byYear = new Map<string, (typeof pts)[number]>()
  for (const p of pts) {
    const year = p.period.slice(0, 4)
    const month = p.period.slice(4)
    const existing = byYear.get(year)
    if (!existing || month > existing.period.slice(4)) byYear.set(year, p)
  }
  return Array.from(byYear.values()).sort((a, b) =>
    a.period.localeCompare(b.period),
  )
})

const latestNetWorth = computed(() => assetTrendPoints.value.at(-1)?.value ?? 0)

const netWorthYoYDelta = computed<number | undefined>(() => {
  const pts = assetTrendPoints.value
  if (pts.length < 2) return undefined
  const curr = pts.at(-1)!.value
  const prev = pts.at(-2)!.value
  if (!prev) return undefined
  return ((curr - prev) / Math.abs(prev)) * 100
})

// Freedom / work-freedom percent values --------------------------------------
const freedomRatioTooltip = computed(() => t('dashboard.freedomTooltip'))

const workFreedomRatioTooltip = computed(() => t('dashboard.workFreedomTooltip'))

const freedomPercentValue = computed(
  () => Math.round(store.freedomRatioCurrent * 1000) / 10,
)

const workFreedomPercentValue = computed(
  () => Math.round(store.workFreedomRatioCurrent * 1000) / 10,
)

// Month-view: feed all 13 points to MetricCard so it computes MoM + YoY badges.
const freedomRatioPercentPoints = computed(() =>
  (store.summaries.freedom_ratio?.points ?? []).map((p) => ({
    period: p.period,
    value: Math.round(p.value * 1000) / 10,
  })),
)

const workFreedomRatioPercentPoints = computed(() =>
  (store.summaries.work_freedom_ratio?.points ?? []).map((p) => ({
    period: p.period,
    value: Math.round(p.value * 1000) / 10,
  })),
)

// Year-view: pre-computed delta against previous year's annual ratio (in pct-points,
// matching MetricCard's static deltaPercent semantics).
const freedomYoYDelta = computed<number | undefined>(() => {
  const prev = store.freedomRatioPrevYear
  if (prev === null) return undefined
  return (store.freedomRatioCurrent - prev) * 100
})

const workFreedomYoYDelta = computed<number | undefined>(() => {
  const prev = store.workFreedomRatioPrevYear
  if (prev === null) return undefined
  return (store.workFreedomRatioCurrent - prev) * 100
})

// Targets CRUD ----------------------------------------------------------------
const targetDialogVisible = ref(false)
const archiveDialogVisible = ref(false)
const targetSubmitting = ref(false)
const editingTarget = ref<TargetSetting | null>(null)

const activeTargets = computed(() => store.targets.filter((t) => t.is_done !== 'Y'))
const archivedTargets = computed(() => store.targets.filter((t) => t.is_done === 'Y'))
const targetFormRef = ref<FormInstance | null>(null)
const targetForm = reactive({
  target_year: dayjs().format('YYYY'),
  setting_value: '',
  is_done: 'N',
})
const targetRules = computed<FormRules>(() => ({
  target_year: [{ required: true, pattern: /^\d{4}$/, message: t('validation.yearFormat'), trigger: 'blur' }],
  setting_value: [{ required: true, message: t('validation.enterContent'), trigger: 'blur' }],
}))

function resetTargetForm() {
  targetForm.target_year = dayjs().format('YYYY')
  targetForm.setting_value = ''
  targetForm.is_done = 'N'
}

function openTargetCreate() {
  editingTarget.value = null
  resetTargetForm()
  targetDialogVisible.value = true
}

function openTargetEdit(t: TargetSetting) {
  editingTarget.value = t
  targetForm.target_year = t.target_year
  targetForm.setting_value = t.setting_value
  targetForm.is_done = t.is_done
  targetDialogVisible.value = true
}

async function submitTarget() {
  if (!targetFormRef.value) return
  const ok = await targetFormRef.value.validate().catch(() => false)
  if (!ok) return
  targetSubmitting.value = true
  try {
    if (editingTarget.value) {
      await updateTarget(editingTarget.value.distinct_number, {
        target_year: targetForm.target_year,
        setting_value: targetForm.setting_value,
        is_done: targetForm.is_done,
      })
      ElMessage.success(t('toast.updated'))
    } else {
      await createTarget({
        target_year: targetForm.target_year,
        setting_value: targetForm.setting_value,
        is_done: targetForm.is_done,
      })
      ElMessage.success(t('toast.created'))
    }
    targetDialogVisible.value = false
    await store.fetchTargets()
  } finally {
    targetSubmitting.value = false
  }
}

async function handleDeleteTarget(targetId: string) {
  await deleteTarget(targetId)
  ElMessage.success(t('toast.deleted'))
  await store.fetchTargets()
}

async function setTargetDone(target: TargetSetting, isDone: 'Y' | 'N') {
  await updateTarget(target.distinct_number, {
    target_year: target.target_year,
    setting_value: target.setting_value,
    is_done: isDone,
  })
  ElMessage.success(isDone === 'Y' ? t('toast.markedDone') : t('toast.restored'))
  await store.fetchTargets()
}

const markTargetDone = (t: TargetSetting) => setTargetDone(t, 'Y')
const markTargetUndone = (t: TargetSetting) => setTargetDone(t, 'N')

// Budget ---------------------------------------------------------------------
const { format: formatMoney } = useMoney()
const moneyFmt = (v: number) => formatMoney(v, { maximumFractionDigits: 0 })

const budgetCardLabel = computed(() => t('dashboard.budgetUsage'))

const budgetUsagePct = computed(() => {
  const b = store.budget
  if (!b || !b.total_planned) return 0
  return Math.round((b.total_actual / b.total_planned) * 1000) / 10
})

const budgetUsageDeltaLabel = computed(() => {
  const b = store.budget
  if (!b || !b.total_planned) {
    return store.viewMode === 'month' ? t('dashboard.noBudgetMonth') : t('dashboard.noBudgetYear')
  }
  return t('dashboard.budgetActualVsPlan', {
    actual: moneyFmt(b.total_actual),
    planned: moneyFmt(b.total_planned),
  })
})

const hasEventBudget = computed(() => {
  const b = store.budget
  return !!b && Array.isArray(b.event_lines) && b.event_lines.length > 0 && b.event_total_planned > 0
})

const eventUsagePct = computed(() => {
  const b = store.budget
  if (!b || !b.event_total_planned) return 0
  return Math.round((b.event_total_actual / b.event_total_planned) * 1000) / 10
})

const eventUsageDeltaLabel = computed(() => {
  const b = store.budget
  if (!b || !b.event_total_planned) return t('dashboard.noEventBudget')
  const ytd = store.viewMode === 'month' ? t('dashboard.eventYtdMonth') : t('dashboard.eventYtdYear')
  return t('dashboard.eventActualVsPlan', {
    ytd,
    actual: moneyFmt(b.event_total_actual),
    planned: moneyFmt(b.event_total_planned),
  })
})

function giftRateClass(rate: number): string {
  if (rate >= 90) return 'bg-error/10 text-error'
  if (rate >= 70) return 'bg-secondary/10 text-secondary'
  return 'bg-primary/10 text-primary'
}

onMounted(() => {
  store.refetchAllForView()
  store.fetchTargets()
  store.fetchUncategorized()
})
</script>
