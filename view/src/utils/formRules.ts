import type { FormItemRule } from 'element-plus'

/** Single required-field rule array for el-form `rules` maps. */
export function requiredRule(
  message: string,
  trigger: 'change' | 'blur' = 'change',
): FormItemRule[] {
  return [{ required: true, message, trigger }]
}
