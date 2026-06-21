import { describe, it, expect, vi, beforeEach } from 'vitest'
import { ref } from 'vue'
import type { FormInstance } from 'element-plus'
import { useCrudDialog } from '@/composables/useCrudDialog'

const { successMock, confirmMock } = vi.hoisted(() => ({
  successMock: vi.fn(),
  confirmMock: vi.fn(),
}))

vi.mock('element-plus', () => ({
  ElMessage: { success: successMock },
}))

vi.mock('@/composables/useConfirm', () => ({
  useConfirm: () => confirmMock,
}))

interface Row {
  id: number
  name: string
}
interface Form {
  id?: number
  name: string
}

function setup(opts: { valid?: boolean; confirm?: boolean; onAfterDelete?: (r: Row) => void } = {}) {
  const validate = vi.fn().mockResolvedValue(opts.valid ?? true)
  const formRef = ref({ validate } as unknown as FormInstance)
  const create = vi.fn().mockResolvedValue(undefined)
  const update = vi.fn().mockResolvedValue(undefined)
  const remove = vi.fn().mockResolvedValue(undefined)
  const refetch = vi.fn().mockResolvedValue(undefined)
  const onAfterDelete = opts.onAfterDelete ?? vi.fn()
  confirmMock.mockResolvedValue(opts.confirm ?? true)
  const crud = useCrudDialog<Row, Form>({
    formRef,
    emptyForm: () => ({ name: '' }),
    toForm: (r) => ({ id: r.id, name: r.name }),
    getId: (r) => r.id,
    create,
    update,
    remove,
    refetch,
    confirmDelete: (r) => ({ title: 'del', message: r.name }),
    onAfterDelete,
  })
  return { crud, formRef, validate, create, update, remove, refetch, onAfterDelete }
}

beforeEach(() => {
  successMock.mockClear()
  confirmMock.mockReset()
})

describe('useCrudDialog', () => {
  it('openCreate sets create mode, a blank form and opens the dialog', () => {
    const { crud } = setup()
    crud.openCreate()
    expect(crud.formMode.value).toBe('create')
    expect(crud.editingId.value).toBeNull()
    expect(crud.form.value).toEqual({ name: '' })
    expect(crud.dialogVisible.value).toBe(true)
  })

  it('openEdit loads the row into the form and records its id', () => {
    const { crud } = setup()
    crud.openEdit({ id: 7, name: 'Acme' })
    expect(crud.formMode.value).toBe('edit')
    expect(crud.editingId.value).toBe(7)
    expect(crud.form.value).toEqual({ id: 7, name: 'Acme' })
    expect(crud.dialogVisible.value).toBe(true)
  })

  it('submit in create mode calls create, toasts, closes and refetches', async () => {
    const { crud, create, update, refetch } = setup()
    crud.openCreate()
    crud.form.value = { name: 'New' }
    await crud.submit()
    expect(create).toHaveBeenCalledWith({ name: 'New' })
    expect(update).not.toHaveBeenCalled()
    expect(successMock).toHaveBeenCalledWith('新增成功')
    expect(crud.dialogVisible.value).toBe(false)
    expect(refetch).toHaveBeenCalled()
    expect(crud.submitting.value).toBe(false)
  })

  it('submit in edit mode calls update with the recorded id', async () => {
    const { crud, create, update } = setup()
    crud.openEdit({ id: 42, name: 'Old' })
    await crud.submit()
    expect(update).toHaveBeenCalledWith(42, { id: 42, name: 'Old' })
    expect(create).not.toHaveBeenCalled()
    expect(successMock).toHaveBeenCalledWith('更新成功')
  })

  it('submit does nothing when validation fails', async () => {
    const { crud, create, update } = setup({ valid: false })
    crud.openCreate()
    await crud.submit()
    expect(create).not.toHaveBeenCalled()
    expect(update).not.toHaveBeenCalled()
    expect(crud.dialogVisible.value).toBe(true)
    expect(crud.submitting.value).toBe(false)
  })

  it('submit returns early when no form ref is bound', async () => {
    const { crud, formRef, create } = setup()
    formRef.value = undefined as unknown as FormInstance
    crud.openCreate()
    await crud.submit()
    expect(create).not.toHaveBeenCalled()
  })

  it('remove deletes after confirmation, then cleans up and refetches', async () => {
    const onAfterDelete = vi.fn()
    const { crud, remove, refetch } = setup({ confirm: true, onAfterDelete })
    const row = { id: 5, name: 'Gone' }
    await crud.remove(row)
    expect(confirmMock).toHaveBeenCalled()
    expect(remove).toHaveBeenCalledWith(5)
    expect(successMock).toHaveBeenCalledWith('已刪除')
    expect(onAfterDelete).toHaveBeenCalledWith(row)
    expect(refetch).toHaveBeenCalled()
  })

  it('remove aborts when the confirmation is cancelled', async () => {
    const { crud, remove } = setup({ confirm: false })
    await crud.remove({ id: 9, name: 'Keep' })
    expect(remove).not.toHaveBeenCalled()
  })
})
