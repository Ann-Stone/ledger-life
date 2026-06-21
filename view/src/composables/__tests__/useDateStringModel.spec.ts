import { describe, it, expect } from 'vitest'
import { ref } from 'vue'
import { useDateStringModel } from '@/composables/useDateStringModel'

describe('useDateStringModel', () => {
  it('reads a YYYYMMDD string as a Date', () => {
    const field = ref('20260415')
    const model = useDateStringModel(
      () => field.value,
      (v) => {
        field.value = v ?? ''
      },
    )
    expect(model.value).toBeInstanceOf(Date)
    expect(model.value!.getFullYear()).toBe(2026)
    expect(model.value!.getMonth()).toBe(3)
    expect(model.value!.getDate()).toBe(15)
  })

  it('reads empty string as null', () => {
    const field = ref('')
    const model = useDateStringModel(
      () => field.value,
      (v) => {
        field.value = v ?? ''
      },
    )
    expect(model.value).toBeNull()
  })

  it('writes a Date back as YYYYMMDD', () => {
    const field = ref('')
    const model = useDateStringModel(
      () => field.value,
      (v) => {
        field.value = v ?? ''
      },
    )
    model.value = new Date(2026, 11, 31)
    expect(field.value).toBe('20261231')
  })

  it('surfaces null on clear so callers choose the coercion', () => {
    // ''-coercing caller (most form fields)
    const emptyCoerced = ref('20260101')
    const m1 = useDateStringModel(
      () => emptyCoerced.value,
      (v) => {
        emptyCoerced.value = v ?? ''
      },
    )
    m1.value = null
    expect(emptyCoerced.value).toBe('')

    // null-keeping caller (loan grace_expire_date)
    const nullKept = ref<string | null>('20260101')
    const m2 = useDateStringModel(
      () => nullKept.value,
      (v) => {
        nullKept.value = v
      },
    )
    m2.value = null
    expect(nullKept.value).toBeNull()
  })
})
