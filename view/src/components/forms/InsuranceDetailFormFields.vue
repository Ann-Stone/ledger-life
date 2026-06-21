<!--
  Insurance journal (premium/claim) detail form fields, shared by:
    1. OtherAssetsView (mode="asset-manage")  — full editor for an existing
       policy's detail row; `insurance_id` displayed as a disabled input above.
    2. CashFlowView    (mode="cashflow-sync") — the journal already supplies
       amount (= spending), date and memo, so this mode hides those rows and
       only asks for the execution type.

  The parent owns the form state object (v-model) and the `insurance_id` picker.
  Mirrors StockDetailFormFields.vue.
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useDateStringModel } from '@/composables/useDateStringModel'

export interface InsuranceDetailFormState {
  distinct_number?: number
  insurance_id: string
  insurance_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

const props = defineProps<{
  modelValue: InsuranceDetailFormState
  mode: 'asset-manage' | 'cashflow-sync'
  showInsuranceIdInput?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: InsuranceDetailFormState): void
}>()

const { t } = useI18n()

const form = computed({
  get: () => props.modelValue,
  set: (v) => emit('update:modelValue', v),
})

const formDate = useDateStringModel(
  () => form.value.excute_date,
  (date) => {
    form.value = { ...form.value, excute_date: date ?? '' }
  },
)

const isCashflow = computed(() => props.mode === 'cashflow-sync')
</script>

<template>
  <el-form-item v-if="showInsuranceIdInput" :label="t('forms.insuranceId')">
    <el-input :model-value="form.insurance_id" disabled />
  </el-form-item>

  <el-form-item v-if="!isCashflow" :label="t('common.date')" prop="excute_date">
    <el-date-picker
      v-model="formDate"
      type="date"
      format="YYYY/MM/DD"
      :clearable="false"
      style="width: 100%"
    />
  </el-form-item>

  <el-form-item :label="t('common.type')" prop="insurance_excute_type">
    <el-select v-model="form.insurance_excute_type" style="width: 100%">
      <el-option :label="t('forms.insurancePay')" value="pay" />
      <el-option :label="t('forms.insuranceCash')" value="cash" />
      <el-option :label="t('forms.insuranceReturn')" value="return" />
      <el-option :label="t('forms.insuranceExpect')" value="expect" />
    </el-select>
  </el-form-item>

  <el-form-item v-if="!isCashflow" :label="t('common.amount')" prop="excute_price">
    <el-input-number
      v-model="form.excute_price"
      :precision="2"
      :step="100"
      controls-position="right"
      style="width: 100%"
    />
  </el-form-item>
  <p v-else class="text-xs text-on-surface-variant mt-1">
    {{ t('forms.amountAutoHint') }}
  </p>

  <el-form-item v-if="!isCashflow" :label="t('common.note')">
    <el-input
      v-model="form.memo"
      type="textarea"
      :rows="2"
      :placeholder="t('common.optional')"
    />
  </el-form-item>
</template>

<script lang="ts">
import type { FormRules } from 'element-plus'
import { requiredRule } from '@/utils/formRules'

type TranslateFn = (key: string) => string

// Validation rules — exported as factory functions so parents can build them
// with their own i18n `t` (messages re-evaluate on locale switch when the
// caller wraps these in a `computed`).
export function insuranceDetailFullRules(t: TranslateFn): FormRules {
  return {
    excute_date: requiredRule(t('validation.pickDate')),
    insurance_excute_type: requiredRule(t('validation.pickType')),
    excute_price: requiredRule(t('validation.enterAmount'), 'blur'),
  }
}

export function insuranceDetailCashflowRules(t: TranslateFn): FormRules {
  return {
    insurance_excute_type: requiredRule(t('validation.pickType')),
  }
}
</script>
