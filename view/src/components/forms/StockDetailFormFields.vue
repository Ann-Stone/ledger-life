<!--
  Stock transaction detail form fields, shared by:
    1. OtherAssetsView (mode="asset-manage")  — full editor for an existing
       holding; `stock_id` displayed as a disabled input above the fields.
    2. CashFlowView    (mode="cashflow-sync") — the journal already supplies
       price (= spending), settling account (= spend_way), date and memo, so
       this mode hides those rows and only asks for type + share count.

  The parent owns the form state object (v-model) and the `stock_id` picker.
-->
<script setup lang="ts">
import { computed } from 'vue'
import { useDateStringModel } from '@/composables/useDateStringModel'

export interface StockDetailFormState {
  distinct_number?: number
  stock_id: string
  excute_type: string
  excute_amount: number
  excute_price: number
  excute_date: string
  account_id: string
  account_name: string
  memo?: string | null
}

type StockExcuteType = 'buy' | 'sell' | 'stock' | 'cash'

const props = defineProps<{
  modelValue: StockDetailFormState
  mode: 'asset-manage' | 'cashflow-sync'
  showStockIdInput?: boolean
  // Restrict the type dropdown (e.g. ['cash'] for the dividend-income flow).
  // Omitted = all four types, the buy/sell default.
  allowedTypes?: StockExcuteType[]
}>()

const emit = defineEmits<{
  (e: 'update:modelValue', value: StockDetailFormState): void
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

const ALL_TYPE_OPTIONS: { value: StockExcuteType; labelKey: string }[] = [
  { value: 'buy', labelKey: 'forms.stockBuy' },
  { value: 'sell', labelKey: 'forms.stockSell' },
  { value: 'stock', labelKey: 'forms.stockStockDividend' },
  { value: 'cash', labelKey: 'forms.stockCashDividend' },
]
const typeOptions = computed(() =>
  props.allowedTypes
    ? ALL_TYPE_OPTIONS.filter((o) => props.allowedTypes!.includes(o.value))
    : ALL_TYPE_OPTIONS,
)
</script>

<template>
  <el-form-item v-if="showStockIdInput" :label="t('forms.holdingId')">
    <el-input :model-value="form.stock_id" disabled />
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

  <el-form-item :label="t('common.type')" prop="excute_type">
    <el-select v-model="form.excute_type" style="width: 100%">
      <el-option
        v-for="o in typeOptions"
        :key="o.value"
        :label="t(o.labelKey)"
        :value="o.value"
      />
    </el-select>
  </el-form-item>

  <el-form-item :label="t('forms.quantity')" prop="excute_amount">
    <el-input-number
      v-model="form.excute_amount"
      :precision="2"
      :step="1"
      controls-position="right"
      style="width: 100%"
    />
    <p v-if="isCashflow" class="text-xs text-on-surface-variant mt-1">
      {{ t('forms.cashDividendHint') }}
    </p>
  </el-form-item>

  <el-form-item v-if="!isCashflow" :label="t('forms.unitPrice')" prop="excute_price">
    <el-input-number
      v-model="form.excute_price"
      :precision="2"
      :step="1"
      controls-position="right"
      style="width: 100%"
    />
  </el-form-item>

  <template v-if="!isCashflow">
    <el-form-item :label="t('forms.accountId')" prop="account_id">
      <el-input v-model="form.account_id" :placeholder="t('forms.accountIdPlaceholder')" />
    </el-form-item>
    <el-form-item :label="t('forms.accountName')" prop="account_name">
      <el-input v-model="form.account_name" :placeholder="t('forms.accountNamePlaceholder')" />
    </el-form-item>
    <el-form-item :label="t('common.note')">
      <el-input
        v-model="form.memo"
        type="textarea"
        :rows="2"
        :placeholder="t('common.optional')"
      />
    </el-form-item>
  </template>
</template>

<script lang="ts">
import type { FormRules } from 'element-plus'
import { requiredRule } from '@/utils/formRules'

type TranslateFn = (key: string) => string

// Validation rules — exported as factory functions so parents can build them
// with their own i18n `t` (messages re-evaluate on locale switch when the
// caller wraps these in a `computed`).
export function stockDetailFullRules(t: TranslateFn): FormRules {
  return {
    excute_date: requiredRule(t('validation.pickDate')),
    excute_type: requiredRule(t('validation.pickType')),
    excute_amount: requiredRule(t('validation.enterQuantity'), 'blur'),
    excute_price: requiredRule(t('validation.enterUnitPrice'), 'blur'),
    account_id: requiredRule(t('validation.enterAccountId'), 'blur'),
    account_name: requiredRule(t('validation.enterAccountName'), 'blur'),
  }
}

export function stockDetailCashflowRules(t: TranslateFn): FormRules {
  return {
    excute_type: requiredRule(t('validation.pickType')),
  }
}
</script>
