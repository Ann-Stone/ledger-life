import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import RowActions from '@/components/ui/RowActions.vue'
import { testI18n } from '@/test/i18n'

// Element Plus is not globally registered in the test env (see src/test/setup.ts),
// so stub el-button with a plain <button> that forwards clicks.
const stubs = {
  'el-button': {
    name: 'ElButton',
    // Mirror Element Plus's ElButton prop types so the bare `link` attribute
    // coerces to a real boolean (matching `<el-button link>` in production).
    props: { type: String, link: Boolean, size: String, icon: null },
    emits: ['click'],
    template: '<button :data-type="type" :data-link="link" @click="$emit(\'click\')"><slot /></button>',
  },
}

describe('RowActions', () => {
  it('emits edit / delete when the two buttons are clicked', async () => {
    const wrapper = mount(RowActions, { global: { stubs, plugins: [testI18n()] } })
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    await buttons[0]!.trigger('click')
    await buttons[1]!.trigger('click')
    expect(wrapper.emitted('edit')).toHaveLength(1)
    expect(wrapper.emitted('delete')).toHaveLength(1)
  })

  it('renders default 編輯 / 刪除 labels', () => {
    const wrapper = mount(RowActions, { global: { stubs, plugins: [testI18n()] } })
    expect(wrapper.text()).toContain('編輯')
    expect(wrapper.text()).toContain('刪除')
  })

  it('honours custom editText / deleteText', () => {
    const wrapper = mount(RowActions, {
      props: { editText: '修改', deleteText: '移除' },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.text()).toContain('修改')
    expect(wrapper.text()).toContain('移除')
  })

  it('renders link-style buttons for the link variant', () => {
    const wrapper = mount(RowActions, {
      props: { variant: 'link' },
      global: { stubs, plugins: [testI18n()] },
    })
    const buttons = wrapper.findAll('button')
    expect(buttons).toHaveLength(2)
    expect(buttons[0]!.attributes('data-link')).toBe('true')
  })

  it('renders the default slot after the action pair', () => {
    const wrapper = mount(RowActions, {
      slots: { default: '<span class="extra">明細</span>' },
      global: { stubs, plugins: [testI18n()] },
    })
    expect(wrapper.find('.extra').exists()).toBe(true)
  })
})
