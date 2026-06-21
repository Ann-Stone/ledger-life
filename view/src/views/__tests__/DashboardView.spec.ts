import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { testI18n } from '@/test/i18n'

// Stub vue-echarts so jsdom-incompatible canvas paths never execute.
vi.mock('vue-echarts', () => ({
  default: { name: 'VChart', render: () => null },
}))

import DashboardView from '@/views/DashboardView.vue'
import AssetTrendChart from '@/components/charts/AssetTrendChart.vue'
import MetricCard from '@/components/ui/MetricCard.vue'
import { useDashboardStore } from '@/stores/dashboard'

function makeSummary(type: string, n: number) {
  return {
    type,
    points: Array.from({ length: n }, (_, i) => ({
      period: `2025${String((i % 12) + 1).padStart(2, '0')}`,
      value:
        type === 'freedom_ratio' || type === 'work_freedom_ratio'
          ? 0.2 + i * 0.01
          : 1000 + i * 100,
      breakdown:
        type === 'freedom_ratio'
          ? { income: 100, fixed_expenses: 75 }
          : type === 'work_freedom_ratio'
            ? { passive: 30, active: 70 }
            : {
                accounts: 200,
                stocks: 300,
                estates: 500,
                insurances: 100,
                loans: -50,
                cards: -50,
              },
    })),
  }
}

function elementPlusStubs() {
  return {
    'el-skeleton': true,
    'el-table': true,
    'el-table-column': true,
    'el-button': true,
    'el-icon': { template: '<span><slot /></span>' },
    'el-popconfirm': true,
    'el-form': true,
    'el-form-item': true,
    'el-input': true,
    'el-input-number': true,
    'el-switch': true,
    'el-dialog': true,
  }
}

describe('DashboardView', () => {
  it('mounts with 12-point summaries and shows trend chart + three metric cards', async () => {
    const wrapper = mount(DashboardView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: true,
            initialState: {
              dashboard: {
                summaries: {
                  asset_debt_trend: makeSummary('asset_debt_trend', 12),
                  freedom_ratio: makeSummary('freedom_ratio', 12),
                  work_freedom_ratio: makeSummary('work_freedom_ratio', 12),
                  spending: null,
                },
                summariesLoading: {
                  asset_debt_trend: false,
                  freedom_ratio: false,
                  work_freedom_ratio: false,
                  spending: false,
                },
                alarms: [],
                alarmsLoading: false,
                targets: [],
                targetsLoading: false,
                budget: null,
                budgetLoading: false,
                gifts: [],
                giftsLoading: false,
              },
            },
          }),
          testI18n(),
        ],
        stubs: elementPlusStubs(),
      },
    })

    // Rolling-window getters live on the store proxy. createTestingPinia does
    // not snapshot getters from initialState; force-evaluate via the store.
    const store = useDashboardStore()
    void store.freedomRatioCurrent
    void store.workFreedomRatioCurrent

    expect(wrapper.text()).not.toContain('本期支出')
    expect(wrapper.findComponent(AssetTrendChart).exists()).toBe(true)
    expect(wrapper.text()).toContain('工作自由度')
    expect(wrapper.findAllComponents(MetricCard).length).toBeGreaterThanOrEqual(3)
  })
})
