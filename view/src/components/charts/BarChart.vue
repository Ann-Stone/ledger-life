<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import {
  BarChart as EchartsBarChart,
  LineChart as EchartsLineChart,
} from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '@/stores/app'
import { getChartColors } from '@/utils/chartTheme'

use([
  CanvasRenderer,
  EchartsBarChart,
  EchartsLineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
])

const props = withDefaults(
  defineProps<{
    xData: string[]
    series: Array<{ name: string; data: number[]; type?: 'bar' | 'line'; stack?: string }>
    height?: string
  }>(),
  { height: '300px' },
)

const appStore = useAppStore()

const option = computed(() => {
  void appStore.theme // reactive dependency — recomputes on theme toggle
  return {
    color: getChartColors(),
    tooltip: { trigger: 'axis', axisPointer: { type: 'shadow' } },
    legend: { data: props.series.map((s) => s.name) },
    grid: { left: 40, right: 20, top: 40, bottom: 30, containLabel: true },
    xAxis: { type: 'category', data: props.xData },
    yAxis: { type: 'value' },
    series: props.series.map((s) => ({
      name: s.name,
      type: s.type ?? 'bar',
      data: s.data,
      // Bars sharing a `stack` key pile up (e.g. fixed + variable expense).
      ...(s.stack ? { stack: s.stack } : {}),
      // A line series (e.g. net balance) overlays the bars; smooth it and lift
      // it above the bars so the trend reads clearly.
      ...(s.type === 'line'
        ? { smooth: true, symbol: 'circle', symbolSize: 6, z: 3 }
        : {}),
    })),
  }
})
</script>
