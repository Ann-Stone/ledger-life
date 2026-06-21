<template>
  <v-chart class="chart" :option="option" :style="{ height }" autoresize />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { PieChart as EchartsPieChart } from 'echarts/charts'
import {
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
} from 'echarts/components'
import VChart from 'vue-echarts'
import { useAppStore } from '@/stores/app'
import { getChartColors } from '@/utils/chartTheme'

use([
  CanvasRenderer,
  EchartsPieChart,
  TooltipComponent,
  LegendComponent,
  GraphicComponent,
])

const props = withDefaults(
  defineProps<{
    data: Array<{ name: string; value: number }>
    centerText?: string
    height?: string
  }>(),
  { height: '300px' },
)

const appStore = useAppStore()

const option = computed(() => {
  void appStore.theme // reactive dependency — recomputes on theme toggle

  const centerFill = getComputedStyle(document.documentElement)
    .getPropertyValue('--ds-primary-container')
    .trim()

  const graphic = props.centerText
    ? [
        {
          type: 'text',
          left: 'center',
          top: 'middle',
          style: {
            text: props.centerText,
            fill: centerFill,
            fontSize: 18,
            fontWeight: 600,
          },
        },
      ]
    : undefined

  return {
    color: getChartColors(),
    tooltip: { trigger: 'item' },
    legend: { bottom: 0 },
    graphic,
    series: [
      {
        type: 'pie',
        radius: ['40%', '70%'],
        center: ['50%', '45%'],
        avoidLabelOverlap: true,
        label: { show: false },
        data: props.data,
      },
    ],
  }
})
</script>
