<!--
  Loan repayment detail fields, used only by CashFlowView (mode="cashflow-sync").

  A repayment splits into 本金 (principal) + 利息 (interest), both POSITIVE
  magnitudes. The parent owns the form state (v-model) and the loan picked as the
  journal's sub-category; the main 金額 field auto-fills to −(principal+interest)
  and is shown read-only there. The backend stores each non-zero portion as its
  own Loan_Journal row.
-->
<script setup lang="ts">
import { computed } from 'vue'

export interface LoanDetailFormState {
  principal: number
  interest: number
}

const props = defineProps<{
  modelValue: LoanDetailFormState
  mode: 'cashflow-sync'
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: LoanDetailFormState): void
}>()

const { t } = useI18n()

const principal = computed({
  get: () => props.modelValue.principal,
  set: (v) => emit('update:modelValue', { ...props.modelValue, principal: Number(v ?? 0) }),
})
const interest = computed({
  get: () => props.modelValue.interest,
  set: (v) => emit('update:modelValue', { ...props.modelValue, interest: Number(v ?? 0) }),
})

const total = computed(() => Number(props.modelValue.principal ?? 0) + Number(props.modelValue.interest ?? 0))
</script>

<template>
  <el-form-item :label="t('forms.loanPrincipal')" prop="principal">
    <el-input-number
      v-model="principal"
      :min="0"
      :precision="2"
      :step="1000"
      controls-position="right"
      style="width: 100%"
    />
  </el-form-item>

  <el-form-item :label="t('forms.loanInterest')" prop="interest">
    <el-input-number
      v-model="interest"
      :min="0"
      :precision="2"
      :step="100"
      controls-position="right"
      style="width: 100%"
    />
    <p class="text-xs text-on-surface-variant mt-1">
      {{ t('forms.loanSplitHint', { total: total.toLocaleString() }) }}
    </p>
  </el-form-item>
</template>

<script lang="ts">
import type { FormRules } from 'element-plus'

type TranslateFn = (key: string) => string

// Validation rules for the cashflow-sync loan split. The cross-field check
// (principal + interest > 0, and == |amount|) is enforced in CashFlowView's
// submit and again by the backend; here we only require non-negative numbers.
export function loanDetailCashflowRules(_t: TranslateFn): FormRules {
  return {}
}
</script>
