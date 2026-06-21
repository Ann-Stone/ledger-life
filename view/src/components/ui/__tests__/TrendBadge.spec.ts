import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import TrendBadge from '@/components/ui/TrendBadge.vue'

describe('TrendBadge', () => {
  it('renders the label when provided', () => {
    const wrapper = mount(TrendBadge, {
      props: { value: 1.5, label: 'MoM' },
      global: { stubs: { 'el-icon': { template: '<span><slot /></span>' } } },
    })
    expect(wrapper.text()).toContain('MoM')
    expect(wrapper.text()).toContain('1.5%')
  })

  it('omits the label span when no label prop is passed', () => {
    const wrapper = mount(TrendBadge, {
      props: { value: -2.3 },
      global: { stubs: { 'el-icon': { template: '<span><slot /></span>' } } },
    })
    expect(wrapper.text()).not.toContain('MoM')
    expect(wrapper.text()).not.toContain('YoY')
    expect(wrapper.text()).toContain('2.3%')
  })
})
