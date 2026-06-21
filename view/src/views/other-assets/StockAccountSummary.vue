<template>
  <div v-if="summaries.length > 0" class="flex flex-col gap-1.5">
    <span class="text-xs text-on-surface-variant">{{ t('otherAssets.accountSummary') }}</span>
    <div class="flex flex-wrap gap-2">
      <button
        v-for="s in summaries"
        :key="s.account"
        type="button"
        class="flex flex-col items-start gap-0.5 rounded-md border px-3 py-1.5 text-left transition"
        :class="
          activeAccount === s.account
            ? 'border-primary bg-primary/10'
            : 'border-outline-variant hover:border-primary hover:bg-primary/5'
        "
        @click="toggle(s.account)"
      >
        <span class="text-sm font-medium text-on-surface">
          {{ s.account || t('otherAssets.accountUnknown') }}
        </span>
        <span class="flex items-center gap-2 text-xs text-on-surface-variant tabular-nums">
          <span>{{ t('otherAssets.sumShares') }} {{ formatShares(s.shares) }}</span>
          <span class="text-outline-variant">·</span>
          <span class="flex items-center gap-1">
            {{ t('otherAssets.colCost') }}
            <MoneyDisplay :amount="s.cost" :currency="currency" size="sm" />
          </span>
          <span class="text-outline-variant">·</span>
          <span class="flex items-center gap-1">
            {{ t('otherAssets.sumAvgPrice') }}
            <MoneyDisplay v-if="s.avgPrice != null" :amount="s.avgPrice" :currency="currency" size="sm" />
            <span v-else>—</span>
          </span>
        </span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useI18n } from 'vue-i18n'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import type { StockJournal } from '@/types/models'
import { computeAccountSummaries } from './stockAccountSummary'

const props = withDefaults(
  defineProps<{
    rows: StockJournal[]
    currency?: string
    /** Currently applied account filter, so the matching chip can highlight. */
    activeAccount?: string | null
  }>(),
  { currency: 'TWD', activeAccount: null },
)

const emit = defineEmits<{ (e: 'select-account', account: string | null): void }>()

const { t } = useI18n()

const summaries = computed(() => computeAccountSummaries(props.rows))

// Click a chip to filter to that account; click the active chip again to clear.
function toggle(account: string) {
  emit('select-account', props.activeAccount === account ? null : account)
}

function formatShares(shares: number): string {
  return shares.toLocaleString('en-US', { maximumFractionDigits: 6 })
}
</script>
