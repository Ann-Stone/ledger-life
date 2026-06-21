import { ElMessageBox } from 'element-plus'
import { i18n } from '@/i18n'

export type ConfirmType = 'warning' | 'info' | 'error'

export interface ConfirmOptions {
  title: string
  message: string
  type?: ConfirmType
}

export function useConfirm() {
  return async (opts: ConfirmOptions): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(opts.message, opts.title, {
        confirmButtonText: i18n.global.t('common.submit'),
        cancelButtonText: i18n.global.t('common.cancel'),
        type: opts.type ?? 'warning',
      })
      return true
    } catch {
      return false
    }
  }
}
