<template>
  <div
    class="flex flex-col gap-3 rounded-xl p-5 md:p-6 bg-surface-container border border-outline-variant shadow-sm"
  >
    <div class="flex justify-between items-start">
      <div class="flex items-center gap-1.5">
        <p class="text-on-surface-variant text-sm font-semibold uppercase tracking-wider">
          {{ label }}
        </p>
        <el-tooltip
          v-if="tooltip"
          :content="tooltip"
          placement="top"
          effect="dark"
          :show-after="150"
          raw-content
        >
          <el-icon class="text-on-surface-variant/70 hover:text-on-surface cursor-help">
            <QuestionFilled />
          </el-icon>
        </el-tooltip>
      </div>
      <el-icon v-if="icon" :class="iconClass">
        <component :is="icon" />
      </el-icon>
    </div>

    <span
      v-if="format === 'percent'"
      class="tabular-nums text-3xl font-bold text-on-surface"
    >
      {{ percentText }}
    </span>
    <MoneyDisplay
      v-else
      :amount="amount"
      :currency="currency"
      size="lg"
      class="text-on-surface"
    />

    <div v-if="usePoints" class="flex flex-wrap items-center gap-1.5 mt-2">
      <TrendBadge
        v-if="momDelta !== undefined"
        :value="momDelta"
        :tone="badgeTone"
        label="MoM"
      />
      <TrendBadge
        v-if="yoyDelta !== undefined"
        :value="yoyDelta"
        :tone="badgeTone"
        label="YoY"
      />
    </div>
    <div v-else-if="hasDelta" class="flex items-center gap-1.5 mt-2">
      <TrendBadge
        v-if="deltaPercent !== undefined"
        :value="deltaPercent"
        :tone="badgeTone"
      />
      <span
        v-if="deltaLabel"
        class="text-on-surface-variant text-xs"
      >
        {{ deltaLabel }}
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'
import { QuestionFilled } from '@element-plus/icons-vue'
import MoneyDisplay from './MoneyDisplay.vue'
import TrendBadge from './TrendBadge.vue'

/**
 * When both `points` and `deltaPercent` are passed, `points` wins:
 * MoM / YoY tags are derived from the points array and the static delta
 * props are ignored.
 */
const props = withDefaults(
  defineProps<{
    label: string
    amount: number
    currency?: string
    deltaPercent?: number
    deltaLabel?: string
    icon?: Component
    tone?: 'primary' | 'rose'
    format?: 'currency' | 'percent'
    /** When format='percent', keep the sign instead of showing |value| (e.g. negative savings rate). */
    signed?: boolean
    points?: Array<{ period: string; value: number }>
    /** Tooltip shown on hover next to label (HTML allowed via raw-content). */
    tooltip?: string
  }>(),
  {
    currency: 'TWD',
    tone: 'primary',
    format: 'currency',
    signed: false,
  },
)

const iconClass = computed(() =>
  props.tone === 'rose' ? 'text-secondary' : 'text-primary',
)

const badgeTone = computed<'positive' | 'negative' | 'auto'>(() => {
  if (props.tone === 'rose') return 'negative'
  return 'auto'
})

const usePoints = computed(() => Array.isArray(props.points))

function pct(curr: number, prev: number | undefined): number | undefined {
  if (prev === undefined || prev === 0) return undefined
  return ((curr - prev) / Math.abs(prev)) * 100
}

const momDelta = computed<number | undefined>(() => {
  const pts = props.points
  if (!pts || pts.length < 2) return undefined
  return pct(pts[pts.length - 1]!.value, pts[pts.length - 2]!.value)
})

const yoyDelta = computed<number | undefined>(() => {
  const pts = props.points
  if (!pts || pts.length < 13) return undefined
  return pct(pts[pts.length - 1]!.value, pts[pts.length - 13]!.value)
})

const hasDelta = computed(
  () => props.deltaPercent !== undefined || !!props.deltaLabel,
)

const percentText = computed(() => {
  const value = props.signed ? props.amount : Math.abs(props.amount)
  return `${value.toFixed(1)}%`
})
</script>
