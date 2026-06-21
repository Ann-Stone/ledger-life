import { ref, type Ref } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { useConfirm } from './useConfirm'
import { i18n } from '@/i18n'

/**
 * Options describing how a single entity's create/edit/delete flow behaves.
 *
 * The composable owns the *state machine* (dialog visibility, form mode,
 * submitting flag, editing id, validation → submit → toast → refetch). Anything
 * entity-specific is supplied via callbacks so the same machine serves every
 * page:
 *   - `getId`        absorbs differing primary keys (string `stock_id` vs
 *                    numeric `id`).
 *   - `update`       is a closure, so payload shaping (dropping the PK, picking
 *                    columns) stays at the call site.
 *   - `onAfterDelete` covers extra cleanup such as dropping a cached detail map.
 */
export interface UseCrudDialogOptions<TRow, TForm> {
  /** Form ref used to run Element Plus validation before submit. */
  formRef: Ref<FormInstance | undefined>
  /** Factory for a blank form (create mode / reset). */
  emptyForm: () => TForm
  /** Map an existing row into form state (edit mode). */
  toForm: (row: TRow) => TForm
  /** Extract the primary key passed to `update` / `remove`. */
  getId: (row: TRow) => string | number
  create: (form: TForm) => Promise<unknown>
  update: (id: string | number, form: TForm) => Promise<unknown>
  remove: (id: string | number) => Promise<unknown>
  /** Reload the list after a successful create / update / delete. */
  refetch: () => unknown | Promise<unknown>
  /** Title + message for the delete confirmation dialog. */
  confirmDelete: (row: TRow) => { title: string; message: string }
  /** Success-toast overrides (defaults: toast.addSuccess / updateSuccess / deleted). */
  messages?: { created?: string; updated?: string; deleted?: string }
  /** Extra cleanup after a successful delete (e.g. drop cached details). */
  onAfterDelete?: (row: TRow) => void
}

export function useCrudDialog<TRow, TForm>(opts: UseCrudDialogOptions<TRow, TForm>) {
  const confirm = useConfirm()

  const dialogVisible = ref(false)
  const formMode = ref<'create' | 'edit'>('create')
  const submitting = ref(false)
  const editingId = ref<string | number | null>(null)
  const form = ref<TForm>(opts.emptyForm()) as Ref<TForm>

  function openCreate() {
    formMode.value = 'create'
    editingId.value = null
    form.value = opts.emptyForm()
    dialogVisible.value = true
  }

  function openEdit(row: TRow) {
    formMode.value = 'edit'
    editingId.value = opts.getId(row)
    form.value = opts.toForm(row)
    dialogVisible.value = true
  }

  async function submit() {
    if (!opts.formRef.value) return
    const valid = await opts.formRef.value.validate().catch(() => false)
    if (!valid) return
    submitting.value = true
    try {
      if (formMode.value === 'create') {
        await opts.create(form.value)
        ElMessage.success(opts.messages?.created ?? i18n.global.t('toast.addSuccess'))
      } else if (editingId.value !== null) {
        await opts.update(editingId.value, form.value)
        ElMessage.success(opts.messages?.updated ?? i18n.global.t('toast.updateSuccess'))
      }
      dialogVisible.value = false
      await opts.refetch()
    } finally {
      submitting.value = false
    }
  }

  async function remove(row: TRow) {
    const { title, message } = opts.confirmDelete(row)
    const ok = await confirm({ title, message, type: 'warning' })
    if (!ok) return
    await opts.remove(opts.getId(row))
    ElMessage.success(opts.messages?.deleted ?? i18n.global.t('toast.deleted'))
    opts.onAfterDelete?.(row)
    await opts.refetch()
  }

  return {
    dialogVisible,
    formMode,
    submitting,
    form,
    editingId,
    openCreate,
    openEdit,
    submit,
    remove,
  }
}
