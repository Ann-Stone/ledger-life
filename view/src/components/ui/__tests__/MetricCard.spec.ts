import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MetricCard from '@/components/ui/MetricCard.vue'
import TrendBadge from '@/components/ui/TrendBadge.vue'
import { testI18n } from '@/test/i18n'

const stubs = {
  'el-icon': { template: '<span><slot /></span>' },
}

function makePoints(n: number, startValue = 100, step = 5) {
  return Array.from({ length: n }, (_, i) => ({
    period: `2025${String((i % 12) + 1).padStart(2, '0')}`,
    value: startValue + step * i,
  }))
}

describe('MetricCard', () => {
  it('renders both MoM and YoY badges given 13+ points', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Net Worth', amount: 1000, points: makePoints(13) },
      global: { stubs, plugins: [testI18n()] },
    })
    const badges = wrapper.findAllComponents(TrendBadge)
    expect(badges).toHaveLength(2)
    expect(wrapper.text()).toContain('MoM')
    expect(wrapper.text()).toContain('YoY')
  })

  it('renders only MoM when given 2 points', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Net Worth', amount: 1000, points: makePoints(2) },
      global: { stubs, plugins: [testI18n()] },
    })
    const badges = wrapper.findAllComponents(TrendBadge)
    expect(badges).toHaveLength(1)
    expect(wrapper.text()).toContain('MoM')
    expect(wrapper.text()).not.toContain('YoY')
  })

  it('renders no badge with 1 point', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Net Worth', amount: 1000, points: makePoints(1) },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.findAllComponents(TrendBadge)).toHaveLength(0)
  })

  it('hides MoM when previous value is 0 (avoid Infinity)', () => {
    const wrapper = mount(MetricCard, {
      props: {
        label: 'Freedom',
        amount: 50,
        points: [
          { period: '202504', value: 0 },
          { period: '202505', value: 50 },
        ],
      },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.findAllComponents(TrendBadge)).toHaveLength(0)
  })

  it('backwards-compat: deltaPercent alone still renders a single tag', () => {
    const wrapper = mount(MetricCard, {
      props: {
        label: 'Spending',
        amount: 1234,
        deltaPercent: 5.7,
        deltaLabel: '較上期',
      },
      global: { stubs, plugins: [testI18n()] },
    })
    const badges = wrapper.findAllComponents(TrendBadge)
    expect(badges).toHaveLength(1)
    expect(badges[0]!.props('label')).toBeUndefined()
    expect(wrapper.text()).toContain('較上期')
  })

  it('format=percent renders amount with % and no TWD prefix', () => {
    const wrapper = mount(MetricCard, {
      props: {
        label: 'Freedom',
        amount: 25.5,
        format: 'percent',
      },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.text()).toContain('25.5%')
    expect(wrapper.text()).not.toContain('TWD')
  })

  it('format=currency (default) keeps MoneyDisplay output', () => {
    const wrapper = mount(MetricCard, {
      props: { label: 'Net Worth', amount: 1234567 },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.text()).toContain('TWD')
  })
})
