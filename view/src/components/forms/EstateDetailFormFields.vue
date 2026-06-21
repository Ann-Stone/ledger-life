<!--
  Estate journal (tax/fee/rent/...) detail form fields, shared by:
    1. OtherAssetsView (mode="asset-manage")  — full editor for an existing
       estate's detail row; `estate_id` displayed as a disabled input above.
    2. CashFlowView    (mode="cashflow-sync") — the journal already supplies
       amount (= spending), date and memo, so this mode hides those rows and
       only asks for the execution type.

  The parent owns the form state object (v-model) and the `estate_id` picker.
  Mirrors StockDetailFormFields.vue.
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useDateStringModel } from '@/composables/useDateStringModel'

export interface EstateDetailFormState {
  distinct_number?: number
  estate_id: string
  estate_excute_type: string
  excute_price: number
  excute_date: string
  memo?: string | null
}

const props = defineProps<{
  modelValue: EstateDetailFormState
  mode: 'asset-manage' | 'cashflow-sync'
  showEstateIdInput?: boolean
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: EstateDetailFormState): void
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
  <el-form-item v-if="showEstateIdInput" :label="t('forms.estateId')">
    <el-input :model-value="form.estate_id" disabled />
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

  <el-form-item :label="t('common.type')" prop="estate_excute_type">
    <el-select v-model="form.estate_excute_type" style="width: 100%">
      <el-option :label="t('forms.estateTax')" value="tax" />
      <el-option :label="t('forms.estateFee')" value="fee" />
      <el-option :label="t('forms.estateInsurance')" value="insurance" />
      <el-option :label="t('forms.estateFix')" value="fix" />
      <el-option :label="t('forms.estateRent')" value="rent" />
      <el-option :label="t('forms.estateDeposit')" value="deposit" />
    </el-select>
  </el-form-item>

  <el-form-item v-if="!isCashflow" :label="t('common.amount')" prop="excute_price">
    <el-input-number
      v-model="form.excute_price"
      :precision="2"
      :step="1000"
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
export function estateDetailFullRules(t: TranslateFn): FormRules {
  return {
    excute_date: requiredRule(t('validation.pickDate')),
    estate_excute_type: requiredRule(t('validation.pickType')),
    excute_price: requiredRule(t('validation.enterAmount'), 'blur'),
  }
}

export function estateDetailCashflowRules(t: TranslateFn): FormRules {
  return {
    estate_excute_type: requiredRule(t('validation.pickType')),
  }
}
</script>
