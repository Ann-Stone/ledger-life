import { describe, it, expect, vi } from 'vitest'
import { mount } from '@vue/test-utils'
import { createTestingPinia } from '@pinia/testing'
import { testI18n } from '@/test/i18n'

// Stub vue-echarts so jsdom-incompatible canvas paths never execute.
vi.mock('vue-echarts', () => ({
  default: { name: 'VChart', render: () => null },
}))

import IncomeStatementView from '@/views/year-report/IncomeStatementView.vue'
import MetricCard from '@/components/ui/MetricCard.vue'

function makeReport() {
  const point = {
    period: '202512',
    active_income: 80000,
    fixed: 25000,
    floating: 18000,
    operating_net: 37000,
    dividend: 3000,
    realized: 5000,
    unrealized: 12000,
    investment_net: 20000,
    comprehensive_net: 57000,
  }
  return {
    type: 'monthly',
    points: [point],
    summary: {
      active_income: 80000,
      fixed: 25000,
      floating: 18000,
      operating_net: 37000,
      dividend: 3000,
      realized: 5000,
      unrealized: 12000,
      investment_net: 20000,
      comprehensive_net: 57000,
    },
  }
}

function elementPlusStubs() {
  return {
    'el-skeleton': true,
    'el-tabs': { template: '<div><slot /></div>' },
    'el-tab-pane': true,
    'el-date-picker': true,
    'el-table': { template: '<div><slot /></div>' },
    'el-table-column': true,
    'el-tooltip': { template: '<span><slot /></span>' },
    'el-icon': { template: '<span><slot /></span>' },
  }
}

describe('IncomeStatementView', () => {
  it('renders the three sections (本業/投資/綜合) with metric cards', () => {
    const wrapper = mount(IncomeStatementView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: true,
            initialState: {
              yearReport: {
                selectedYear: 2025,
                incomeStatementReport: makeReport(),
                incomeStatementLoading: false,
              },
            },
          }),
          testI18n(),
        ],
        stubs: elementPlusStubs(),
      },
    })

    // 本業淨額 / 投資損益 / 綜合損益 cards.
    expect(wrapper.findAllComponents(MetricCard).length).toBe(3)
    expect(wrapper.text()).toContain('損益表')
    expect(wrapper.text()).toContain('本業淨額')
    expect(wrapper.text()).toContain('投資損益')
    expect(wrapper.text()).toContain('綜合損益')
    // Comprehensive total renders (37000 + 20000 = 57000).
    expect(wrapper.text()).toContain('57,000')
  })

  it('shows the empty state when there are no points', () => {
    const wrapper = mount(IncomeStatementView, {
      global: {
        plugins: [
          createTestingPinia({
            createSpy: vi.fn,
            stubActions: true,
            initialState: {
              yearReport: {
                selectedYear: 2025,
                incomeStatementReport: { type: 'monthly', points: [], summary: {} },
                incomeStatementLoading: false,
              },
            },
          }),
          testI18n(),
        ],
        stubs: elementPlusStubs(),
      },
    })

    expect(wrapper.text()).toContain('暫無損益資料')
  })
})
