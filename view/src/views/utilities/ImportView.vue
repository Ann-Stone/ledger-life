<template>
  <div class="flex flex-col gap-6">
    <PageHeader :title="t('import.title')" :subtitle="t('import.subtitle')" />

    <DataListCard :title="t('import.stockTitle')">
      <div class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          {{ t('import.stockDesc') }}
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-date-picker
            v-model="stockPeriod"
            type="month"
            value-format="YYYYMM"
            :placeholder="t('import.periodPlaceholder')"
            style="width: 200px"
          />
          <el-button
            type="primary"
            :loading="stockLoading"
            @click="handleStockPriceImport"
          >
            {{ t('import.stockButton') }}
          </el-button>
        </div>
        <p class="text-xs text-on-surface-muted">
          {{ t('import.stockHint') }}
        </p>
      </div>
    </DataListCard>

    <DataListCard :title="t('import.fxTitle')">
      <div class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          {{ t('import.fxDesc') }}
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-date-picker
            v-model="fxPeriod"
            type="month"
            value-format="YYYYMM"
            :placeholder="t('import.periodPlaceholder')"
            style="width: 200px"
          />
          <el-button
            type="primary"
            :loading="fxLoading"
            @click="handleFxRateImport"
          >
            {{ t('import.fxButton') }}
          </el-button>
        </div>
        <p class="text-xs text-on-surface-muted">
          {{ t('import.fxHint') }}
        </p>
      </div>
    </DataListCard>

    <DataListCard :title="t('import.invoiceTitle')">
      <div v-loading="invoiceLoading" class="p-6 flex flex-col gap-3">
        <p class="text-sm text-on-surface-variant">
          {{ t('import.invoiceDesc') }}
        </p>
        <div class="flex flex-wrap items-center gap-3">
          <el-upload
            ref="invoiceUploadRef"
            class="shrink-0"
            :auto-upload="false"
            :limit="1"
            accept=".csv"
            :on-change="handleInvoiceChange"
            :on-remove="handleInvoiceRemove"
            :on-exceed="handleInvoiceExceed"
          >
            <template #trigger>
              <el-button>{{ t('import.chooseCsv') }}</el-button>
            </template>
          </el-upload>
          <el-button
            type="primary"
            :loading="invoiceLoading"
            :disabled="!invoiceFile"
            @click="handleInvoiceImport"
          >
            {{ t('import.invoiceButton') }}
          </el-button>
        </div>
        <div v-if="invoiceResult" class="flex flex-col gap-1">
          <p class="text-xs text-on-surface-muted">
            {{
              t('import.lastResult', {
                imported: invoiceResult.imported,
                skipped: invoiceResult.skipped,
                failed: invoiceResult.failed,
              })
            }}
          </p>
          <ul
            v-if="invoiceResult.months.length"
            class="flex flex-col gap-0.5 text-xs text-on-surface-muted"
          >
            <li v-for="m in invoiceResult.months" :key="m.month">
              {{ t('import.monthImported', { month: formatMonth(m.month), imported: m.imported })
              }}<span v-if="m.skipped">{{ t('import.monthSkipped', { skipped: m.skipped }) }}</span>
            </li>
          </ul>
        </div>
        <p v-else class="text-xs text-on-surface-muted">
          {{ t('import.invoiceEmptyHint') }}
        </p>
      </div>
    </DataListCard>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, genFileId } from 'element-plus'
import type { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import {
  importStockPrices,
  importFxRates,
  importInvoices,
} from '@/api/utilities'
import type { InvoiceImportResult } from '@/types/models'

const { t } = useI18n()

const stockPeriod = ref<string>('')
const fxPeriod = ref<string>('')

const stockLoading = ref(false)
const fxLoading = ref(false)
const invoiceLoading = ref(false)

const invoiceUploadRef = ref<UploadInstance>()
const invoiceFile = ref<File | null>(null)
const invoiceResult = ref<InvoiceImportResult | null>(null)

// 202603 → 2026/03; leave anything unexpected untouched.
function formatMonth(yyyymm: string): string {
  if (yyyymm.length !== 6) return yyyymm
  return `${yyyymm.slice(0, 4)}/${yyyymm.slice(4, 6)}`
}

async function handleStockPriceImport() {
  stockLoading.value = true
  try {
    const res = await importStockPrices(stockPeriod.value)
    ElMessage.success(res.message || t('import.stockScheduled'))
  } catch {
    ElMessage.error(t('import.stockFailed'))
  } finally {
    stockLoading.value = false
  }
}

async function handleFxRateImport() {
  fxLoading.value = true
  try {
    const res = await importFxRates(fxPeriod.value)
    ElMessage.success(res.message || t('import.fxScheduled'))
  } catch {
    ElMessage.error(t('import.fxFailed'))
  } finally {
    fxLoading.value = false
  }
}

const handleInvoiceChange: UploadProps['onChange'] = (uploadFile) => {
  invoiceFile.value = uploadFile.raw ?? null
  invoiceResult.value = null
}

const handleInvoiceRemove: UploadProps['onRemove'] = () => {
  invoiceFile.value = null
}

// el-upload is capped at one file; picking another replaces the current one.
const handleInvoiceExceed: UploadProps['onExceed'] = (files) => {
  invoiceUploadRef.value?.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  invoiceUploadRef.value?.handleStart(file)
  invoiceFile.value = file
  invoiceResult.value = null
}

async function handleInvoiceImport() {
  if (!invoiceFile.value) {
    ElMessage.warning(t('import.pickCsvFirst'))
    return
  }
  invoiceLoading.value = true
  try {
    const res = await importInvoices(invoiceFile.value)
    invoiceResult.value = res
    const msg = t('import.resultSummary', {
      imported: res.imported,
      skipped: res.skipped,
      failed: res.failed,
    })
    if (res.failed > 0) ElMessage.warning(msg)
    else ElMessage.success(msg)
    invoiceUploadRef.value?.clearFiles()
    invoiceFile.value = null
  } catch {
    ElMessage.error(t('import.invoiceFailed'))
  } finally {
    invoiceLoading.value = false
  }
}
</script>
