<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart } from 'echarts/charts'
import { GridComponent, TooltipComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '@/stores/app'
import { useMoney } from '@/composables/useMoney'

use([CanvasRenderer, BarChart, GridComponent, TooltipComponent])

/**
 * Contribution waterfall: each item is a signed delta drawn from the running
 * cumulative; a final total bar closes back to zero. Rendered as a stacked bar
 * with a transparent placeholder series carrying the offset.
 */
const props = withDefaults(
  defineProps<{
    items: Array<{ name: string; value: number }>
    totalLabel?: string
    height?: string
  }>(),
  { height: '320px' },
)

const appStore = useAppStore()
const { t } = useI18n()
const { format: formatMoney } = useMoney()

const UP = '#34d399' // inflow
const DOWN = '#fb7185' // outflow
const TOTAL = '#818cf8'

const option = computed(() => {
  void appStore.theme // recompute on theme toggle
  const cats: string[] = []
  const placeholder: number[] = []
  const bars: { value: number; itemStyle: { color: string } }[] = []
  const signed: number[] = []
  let cum = 0
  for (const it of props.items) {
    const start = cum
    const end = cum + it.value
    cats.push(it.name)
    placeholder.push(Math.min(start, end))
    bars.push({ value: Math.abs(it.value), itemStyle: { color: it.value >= 0 ? UP : DOWN } })
    signed.push(it.value)
    cum = end
  }
  cats.push(props.totalLabel ?? t('chart.netChange'))
  placeholder.push(Math.min(0, cum))
  bars.push({ value: Math.abs(cum), itemStyle: { color: TOTAL } })
  signed.push(cum)

  return {
    tooltip: {
      trigger: 'axis',
      axisPointer: { type: 'shadow' },
      formatter: (params: Array<{ dataIndex: number }>) => {
        const idx = params[0]!.dataIndex
        const v = signed[idx]!
        const sign = v >= 0 ? '+' : '−'
        return `${cats[idx]}<br/>${sign}${formatMoney(Math.abs(v))}`
      },
    },
    grid: { left: 40, right: 20, top: 20, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: cats },
    yAxis: { type: 'value' },
    series: [
      {
        type: 'bar',
        stack: 'wf',
        itemStyle: { color: 'transparent' },
        emphasis: { itemStyle: { color: 'transparent' } },
        data: placeholder,
        silent: true,
      },
      { type: 'bar', stack: 'wf', data: bars },
    ],
  }
})
</script>
