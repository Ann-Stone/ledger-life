<template>
  <div class="px-6 py-4 flex flex-col gap-3">
    <!-- Header: title + parent-supplied actions (e.g. add-detail button) -->
    <div class="flex items-center justify-between gap-3">
      <span class="text-on-surface font-medium">{{ title }}</span>
      <slot name="actions" />
    </div>

    <el-skeleton v-if="loading" :rows="3" animated />
    <EmptyState v-else-if="rows.length === 0" :message="emptyMessage" />
    <template v-else>
      <!-- Filter bar: type (always) + account (stocks only) -->
      <div class="flex flex-wrap items-center gap-2">
        <el-select
          v-model="typeFilter"
          :placeholder="t('otherAssets.filterByType')"
          clearable
          size="small"
          style="width: 170px"
        >
          <el-option
            v-for="opt in typeOptions"
            :key="opt.value"
            :label="opt.label"
            :value="opt.value"
          />
        </el-select>
        <el-select
          v-if="accountField"
          v-model="accountFilter"
          :placeholder="t('otherAssets.filterByAccount')"
          clearable
          size="small"
          style="width: 200px"
        >
          <el-option v-for="acc in accountOptions" :key="acc" :label="acc" :value="acc" />
        </el-select>
        <span class="text-xs text-on-surface-variant">
          {{ t('otherAssets.detailCount', { shown: filteredRows.length, total: rows.length }) }}
        </span>
      </div>

      <!-- Optional summary (e.g. per-account stock summary). setAccount lets the
           summary drive the account filter. -->
      <slot name="summary" :set-account="setAccount" :account-filter="accountFilter" />

      <EmptyState v-if="filteredRows.length === 0" :message="t('otherAssets.noFilterMatch')" />
      <slot v-else :rows="filteredRows" />
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useI18n } from 'vue-i18n'
import EmptyState from '@/components/ui/EmptyState.vue'
import type { AssetDetailBase } from '@/types/models'

const props = defineProps<{
  title: string
  rows: AssetDetailBase[]
  loading: boolean
  emptyMessage: string
  /** Field name holding the row's type enum (e.g. 'excute_type'). */
  typeField: string
  /** Optional raw-enum → readable label map for the type filter + display. */
  typeLabels?: Record<string, string>
  /** Field name holding the account (e.g. 'account_name'); omit to hide the
   *  account filter (only stock details carry an account). */
  accountField?: string
}>()

const { t } = useI18n()

const typeFilter = ref<string | null>(null)
const accountFilter = ref<string | null>(null)

function rowVal(row: AssetDetailBase, field: string): string {
  return String((row as unknown as Record<string, unknown>)[field] ?? '')
}

const typeOptions = computed(() => {
  const seen = new Set<string>()
  const opts: { value: string; label: string }[] = []
  for (const r of props.rows) {
    const v = rowVal(r, props.typeField)
    if (!v || seen.has(v)) continue
    seen.add(v)
    opts.push({ value: v, label: props.typeLabels?.[v] ?? v })
  }
  return opts
})

const accountOptions = computed(() => {
  if (!props.accountField) return []
  const seen = new Set<string>()
  for (const r of props.rows) {
    const v = rowVal(r, props.accountField)
    if (v) seen.add(v)
  }
  return [...seen]
})

const filteredRows = computed(() => {
  const field = props.accountField
  const filtered = props.rows.filter((r) => {
    if (typeFilter.value && rowVal(r, props.typeField) !== typeFilter.value) return false
    if (field && accountFilter.value && rowVal(r, field) !== accountFilter.value) return false
    return true
  })
  // Newest first; tie-break on distinct_number for a stable order.
  return [...filtered].sort(
    (a, b) => b.excute_date.localeCompare(a.excute_date) || b.distinct_number - a.distinct_number,
  )
})

function setAccount(account: string | null) {
  accountFilter.value = account
}
</script>
