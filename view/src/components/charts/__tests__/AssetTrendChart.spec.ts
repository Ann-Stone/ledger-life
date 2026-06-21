import { describe, it, expect, beforeEach, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { setActivePinia, createPinia } from 'pinia'

// vue-echarts is mounted on real DOM (canvas) which jsdom does not support;
// stub it to a no-op component so we can assert chart-option shape without
// triggering zrender canvas paths.
vi.mock('vue-echarts', () => ({
  default: { name: 'VChart', render: () => null },
}))

import AssetTrendChart from '@/components/charts/AssetTrendChart.vue'
import { testI18n } from '@/test/i18n'
import type { DashboardSummaryPoint } from '@/types/models'

function makePoints(): DashboardSummaryPoint[] {
  return Array.from({ length: 12 }, (_, i) => {
    const month = String((i % 12) + 1).padStart(2, '0')
    return {
      period: `2025${month}`,
      value: 1000 + i * 10,
      breakdown: {
        accounts: 200,
        stocks: 300,
        estates: 500,
        insurances: 100,
        loans: -50,
        cards: -50,
      },
    }
  })
}

describe('AssetTrendChart', () => {
  beforeEach(() => {
    setActivePinia(createPinia())
  })

  it('renders with 12-point fixture and emits chartOption with 7 series', () => {
    const wrapper = mount(AssetTrendChart, {
      props: { points: makePoints() },
      global: { stubs: { 'v-chart': true }, plugins: [testI18n()] },
    })
    const option = (wrapper.vm as unknown as { option: { series: unknown[] } }).option
    expect(option.series).toHaveLength(7)
  })

  it('places net-worth as the last series, no stack, type=line', () => {
    const wrapper = mount(AssetTrendChart, {
      props: { points: makePoints() },
      global: { stubs: { 'v-chart': true }, plugins: [testI18n()] },
    })
    const series = (
      wrapper.vm as unknown as {
        option: {
          series: Array<{ name: string; stack?: string; type: string }>
        }
      }
    ).option.series
    const last = series[series.length - 1]!
    expect(last.name).toBe('淨值')
    expect(last.type).toBe('line')
    expect(last.stack).toBeUndefined()
  })

  it('renders empty axis when given zero points (no crash)', () => {
    const wrapper = mount(AssetTrendChart, {
      props: { points: [] },
      global: { stubs: { 'v-chart': true }, plugins: [testI18n()] },
    })
    const option = (
      wrapper.vm as unknown as {
        option: { xAxis: { data: unknown[] }; series: Array<{ data: unknown[] }> }
      }
    ).option
    expect(option.xAxis.data).toEqual([])
    expect(option.series.every((s) => s.data.length === 0)).toBe(true)
  })
})
