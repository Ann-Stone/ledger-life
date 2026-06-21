import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import SharePercent from '@/components/ui/SharePercent.vue'

describe('SharePercent', () => {
  it('renders the value with one decimal and a percent sign', () => {
    const wrapper = mount(SharePercent, { props: { value: 42.345 } })
    expect(wrapper.text()).toBe('42.3%')
    expect(wrapper.classes()).toContain('tabular-nums')
  })

  it('renders an em-dash for null/undefined', () => {
    expect(mount(SharePercent, { props: { value: null } }).text()).toBe('—')
    expect(mount(SharePercent).text()).toBe('—')
  })

  it('merges caller classes via attribute fallthrough', () => {
    const wrapper = mount(SharePercent, {
      props: { value: 10 },
      attrs: { class: 'text-sm text-on-surface-variant' },
    })
    expect(wrapper.classes()).toContain('tabular-nums')
    expect(wrapper.classes()).toContain('text-sm')
    expect(wrapper.classes()).toContain('text-on-surface-variant')
  })
})
