<template>
  <div
    class="flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-bold"
    :class="toneClass"
  >
    <span v-if="label" class="text-[10px] opacity-70">{{ label }}</span>
    <el-icon class="text-[14px]">
      <Top v-if="isPositive" />
      <Bottom v-else />
    </el-icon>
    <span>{{ formatted }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Top, Bottom } from '@element-plus/icons-vue'

defineOptions({ name: 'TrendBadge' })

const props = withDefaults(
  defineProps<{
    value: number
    tone?: 'positive' | 'negative' | 'auto'
    label?: string
  }>(),
  { tone: 'auto' },
)

const isPositive = computed(() => {
  if (props.tone === 'positive') return true
  if (props.tone === 'negative') return false
  return props.value >= 0
})

const toneClass = computed(() =>
  isPositive.value
    ? 'text-primary bg-primary/10'
    : 'text-secondary bg-secondary/10',
)

const formatted = computed(() => {
  const abs = Math.abs(props.value)
  return `${abs.toFixed(1)}%`
})
</script>
