<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('cashFlow.title')" :subtitle="store.selectedMonth">
      <template #actions>
        <el-date-picker
          v-model="selectedMonthDate"
          type="month"
          :placeholder="t('cashFlow.pickMonth')"
          format="YYYY/MM"
          :clearable="false"
        />
        <el-button :icon="TrendCharts" @click="openStockPriceSnapshot">
          {{ t('cashFlow.stockSnapshot') }}
        </el-button>
        <el-button :icon="Wallet" @click="openInsuranceSnapshot">
          {{ t('cashFlow.surrenderValue') }}
        </el-button>
        <el-button :icon="House" @click="openEstateSnapshot">
          {{ t('cashFlow.estateValuation') }}
        </el-button>
        <el-button type="warning" :loading="settling" @click="confirmSettle">
          {{ t('cashFlow.runSettle') }}
        </el-button>
      </template>
    </PageHeader>

    <section class="flex flex-col gap-4">
      <SectionHeader :title="t('cashFlow.journal')">
        <template #actions>
          <el-button type="primary" :icon="Plus" size="small" @click="openCreateJournal">
            {{ t('common.add') }}
          </el-button>
        </template>
      </SectionHeader>
      <el-skeleton v-if="store.journalsLoading" :rows="5" animated />
      <EmptyState v-else-if="store.journals.length === 0" :message="t('cashFlow.noJournals')" />
      <template v-else>
        <el-alert v-if="uncategorizedCount > 0" type="warning" :closable="false" show-icon>
          <template #title>
            <div class="flex flex-wrap items-center gap-3">
              <span>{{ t('cashFlow.uncategorizedBanner', { count: uncategorizedCount }) }}</span>
              <el-button
                size="small"
                type="warning"
                :plain="!showUncategorizedOnly"
                @click="showUncategorizedOnly = !showUncategorizedOnly"
              >
                {{
                  showUncategorizedOnly
                    ? t('cashFlow.uncategorizedShowAll')
                    : t('cashFlow.uncategorizedShowOnly')
                }}
              </el-button>
            </div>
          </template>
        </el-alert>
        <el-table :data="displayedJournals" stripe border style="width: 100%">
          <el-table-column prop="spend_date" :label="t('cashFlow.colDate')" width="110" />
          <el-table-column :label="t('cashFlow.colAccount')" min-width="140">
            <template #default="{ row }">
              <span>{{ spendWayLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('cashFlow.colCategory')" width="140">
            <template #default="{ row }">
              <el-tag v-if="isUncategorized(row.action_main_type)" type="warning" size="small">
                {{ t('cashFlow.uncategorizedTag') }}
              </el-tag>
              <span v-else>{{ actionMainLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('cashFlow.colSubCategory')" width="140">
            <template #default="{ row }">
              <span>{{ actionSubLabel(row) }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('cashFlow.colAmount')" width="180" align="right">
            <template #default="{ row }">
              <MoneyDisplay
                :amount="row.spending"
                :positive="row.spending > 0 ? true : row.spending < 0 ? false : null"
                size="sm"
              />
            </template>
          </el-table-column>
          <el-table-column prop="note" :label="t('common.note')" min-width="160">
            <template #default="{ row }">
              <span>{{ row.note ?? '' }}</span>
            </template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="180" align="center">
            <template #default="{ row }">
              <div class="flex items-center justify-center gap-2 whitespace-nowrap">
              <el-button size="small" :icon="Edit" @click="editJournal(row)">{{ t('common.edit') }}</el-button>
              <el-popconfirm
                :title="t('cashFlow.confirmDeleteJournal')"
                @confirm="handleDeleteJournal(row.distinct_number)"
              >
                <template #reference>
                  <el-button size="small" type="danger" :icon="Delete">{{ t('common.delete') }}</el-button>
                </template>
              </el-popconfirm>
              </div>
            </template>
          </el-table-column>
        </el-table>

        <div
          class="grid grid-cols-1 md:grid-cols-3 gap-4 rounded-xl border border-outline-variant bg-surface-container p-6"
        >
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">{{ t('cashFlow.monthIncome') }}</p>
            <MoneyDisplay :amount="totalIncome" :positive="true" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">{{ t('cashFlow.monthExpense') }}</p>
            <MoneyDisplay :amount="totalExpense" :positive="false" size="lg" />
          </div>
          <div class="flex flex-col gap-1">
            <p class="text-on-surface-variant text-xs uppercase tracking-wider">{{ t('cashFlow.monthNet') }}</p>
            <MoneyDisplay
              :amount="netTotal"
              :positive="netTotal > 0 ? true : netTotal < 0 ? false : null"
              size="lg"
            />
          </div>
        </div>
      </template>
    </section>

    <section class="flex flex-col gap-4">
      <SectionHeader :title="t('cashFlow.analysis')" />
      <el-tabs v-model="activeChartTab">
        <el-tab-pane :label="t('cashFlow.tabBudget')" name="budget">
          <el-skeleton v-if="store.expenditureBudgetLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.expenditureBudget || store.expenditureBudget.rows.length === 0"
            :message="t('cashFlow.noBudget')"
          />
          <BarChart
            v-else
            :x-data="budgetChart.xData"
            :series="budgetChart.series"
            height="320px"
          />
        </el-tab-pane>
        <el-tab-pane :label="t('cashFlow.tabExpenseRatio')" name="expenditureRatio">
          <el-skeleton v-if="store.expenditureRatioLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.expenditureRatio || store.expenditureRatio.outer.length === 0"
            :message="t('cashFlow.noExpense')"
          />
          <DonutChart v-else :data="store.expenditureRatio.outer" height="320px" />
        </el-tab-pane>
        <el-tab-pane :label="t('cashFlow.tabInvestRatio')" name="investRatio">
          <el-skeleton v-if="store.investRatioLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.investRatio || store.investRatio.items.length === 0"
            :message="t('cashFlow.noInvest')"
          />
          <DonutChart v-else :data="store.investRatio.items" height="320px" />
        </el-tab-pane>
        <el-tab-pane :label="t('cashFlow.tabLiability')" name="liability">
          <el-skeleton v-if="store.liabilityLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!store.liability || store.liability.items.length === 0"
            :message="t('cashFlow.noLiability')"
          />
          <el-table v-else :data="store.liability.items" border>
            <el-table-column prop="credit_card_id" :label="t('cashFlow.colCreditCardId')" width="160" />
            <el-table-column prop="credit_card_name" :label="t('cashFlow.colName')" min-width="160" />
            <el-table-column :label="t('cashFlow.colAmount')" width="200" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" :positive="false" size="sm" />
              </template>
            </el-table-column>
          </el-table>
        </el-tab-pane>
      </el-tabs>
    </section>

    <el-dialog
      v-model="stockPriceSnapshotVisible"
      :title="t('cashFlow.stockSnapshot')"
      width="640px"
    >
      <div class="flex justify-end mb-3">
        <el-button type="primary" :icon="Plus" size="small" @click="openStockPriceDialog()">
          {{ t('cashFlow.addStockPrice') }}
        </el-button>
      </div>
      <el-skeleton v-if="store.stockPricesLoading" :rows="3" animated />
      <EmptyState
        v-else-if="store.stockPrices.length === 0"
        :message="t('cashFlow.noStockSnapshot')"
      />
      <el-table v-else :data="store.stockPrices" border>
        <el-table-column prop="stock_code" :label="t('cashFlow.colCode')" width="120" />
        <el-table-column prop="stock_name" :label="t('cashFlow.colName')" min-width="180" />
        <el-table-column :label="t('cashFlow.colDate')" width="120" align="center">
          <template #default="{ row }">
            <span v-if="row.fetch_date">{{ formatDate(row.fetch_date) }}</span>
            <span v-else class="text-gray-400">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('cashFlow.colClosePrice')" width="180" align="right">
          <template #default="{ row }">
            <MoneyDisplay v-if="row.close_price !== null" :amount="row.close_price" size="sm" />
            <el-button
              v-else
              type="warning"
              size="small"
              link
              :icon="Plus"
              @click="openStockPriceDialog(row.stock_code)"
            >
              {{ t('cashFlow.pending') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <FormDialog
      v-model="stockPriceDialogVisible"
      :title="t('cashFlow.addStockPriceTitle')"
      :loading="stockPriceSubmitting"
      width="520px"
      @submit="submitStockPrice"
    >
      <el-form ref="stockPriceFormRef" :model="stockPriceForm" :rules="stockPriceRules" label-width="120px">
        <el-form-item :label="t('cashFlow.colCode')" prop="stock_code">
          <el-input v-model="stockPriceForm.stock_code" :placeholder="t('cashFlow.stockCodeExample')" />
        </el-form-item>
        <el-form-item :label="t('cashFlow.colDate')" prop="fetch_date">
          <el-date-picker
            v-model="stockPriceFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldOpen')" prop="open_price">
          <el-input-number v-model="stockPriceForm.open_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldHigh')" prop="highest_price">
          <el-input-number v-model="stockPriceForm.highest_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldLow')" prop="lowest_price">
          <el-input-number v-model="stockPriceForm.lowest_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldClose')" prop="close_price">
          <el-input-number v-model="stockPriceForm.close_price" :precision="2" style="width: 100%" />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldAutoFetch')">
          <el-switch v-model="stockPriceForm.trigger_yfinance" />
          <p class="text-xs text-on-surface-variant ml-3">
            {{ t('cashFlow.yfinanceHint') }}
          </p>
        </el-form-item>
      </el-form>
    </FormDialog>

    <el-dialog v-model="insuranceSnapshotVisible" :title="t('cashFlow.insuranceSurrenderTitle')" width="640px">
      <p class="text-on-surface-variant/70 text-sm mb-3">
        {{ t('cashFlow.insuranceSurrenderDesc') }}
      </p>
      <el-skeleton v-if="store.insuranceValuesLoading" :rows="3" animated />
      <EmptyState
        v-else-if="store.insuranceValues.length === 0"
        :message="t('cashFlow.noInsurance')"
      />
      <el-table v-else :data="store.insuranceValues" border>
        <el-table-column prop="insurance_name" :label="t('cashFlow.colInsurance')" min-width="200" />
        <el-table-column :label="t('cashFlow.surrenderValue')" width="200" align="right">
          <template #default="{ row }">
            <MoneyDisplay
              v-if="row.surrender_value !== null"
              :amount="row.surrender_value"
              size="sm"
            />
            <span v-else class="text-on-surface-variant/40">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('cashFlow.colStatus')" width="120" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.recorded" type="success" size="small" effect="plain">{{ t('cashFlow.recordedThisMonth') }}</el-tag>
            <el-tag v-else type="warning" size="small" effect="plain">{{ t('cashFlow.pending') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="120" align="center">
          <template #default="{ row }">
            <el-button size="small" link :icon="Edit" @click="openInsuranceValueDialog(row)">
              {{ t('cashFlow.record') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <FormDialog
      v-model="insuranceValueDialogVisible"
      :title="t('cashFlow.recordSurrenderTitle')"
      :loading="insuranceValueSubmitting"
      width="480px"
      @submit="submitInsuranceValue"
    >
      <el-form ref="insuranceValueFormRef" :model="insuranceValueForm" :rules="insuranceValueRules" label-width="120px">
        <el-form-item :label="t('cashFlow.colInsurance')">
          <span>{{ insuranceValueForm.insurance_name }}</span>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldMonth')">
          <span>{{ store.selectedMonth }}</span>
        </el-form-item>
        <el-form-item :label="t('cashFlow.surrenderValue')" prop="surrender_value">
          <el-input-number
            v-model="insuranceValueForm.surrender_value"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <el-dialog v-model="estateSnapshotVisible" :title="t('cashFlow.estateValuation')" width="780px">
      <div class="flex items-start justify-between gap-3 mb-3">
        <p class="text-on-surface-variant/70 text-sm">
          {{ t('cashFlow.estateValuationDesc') }}
        </p>
        <el-button
          size="small"
          :icon="Refresh"
          :loading="refreshingIndex"
          @click="refreshIndex"
        >
          {{ t('cashFlow.refreshIndex') }}
        </el-button>
      </div>
      <el-skeleton v-if="store.estateValuesLoading" :rows="3" animated />
      <EmptyState v-else-if="store.estateValues.length === 0" :message="t('cashFlow.noEstate')" />
      <el-table v-else :data="store.estateValues" border>
        <el-table-column prop="estate_name" :label="t('cashFlow.colEstate')" min-width="150" />
        <el-table-column :label="t('cashFlow.colMarketValue')" width="150" align="right">
          <template #default="{ row }">
            <MoneyDisplay
              v-if="row.market_value !== null"
              :amount="row.market_value"
              size="sm"
            />
            <span v-else class="text-on-surface-variant/40">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('cashFlow.colSuggestedValue')" width="190" align="right">
          <template #default="{ row }">
            <div
              v-if="suggestedValueFor(row.estate_id) != null"
              class="flex items-center justify-end gap-2"
            >
              <MoneyDisplay :amount="suggestedValueFor(row.estate_id) as number" size="sm" />
              <el-button size="small" link type="primary" @click="applySuggestion(row)">
                {{ t('cashFlow.applySuggestion') }}
              </el-button>
            </div>
            <span v-else class="text-on-surface-variant/40">—</span>
          </template>
        </el-table-column>
        <el-table-column :label="t('cashFlow.colStatus')" width="100" align="center">
          <template #default="{ row }">
            <el-tag v-if="row.recorded" type="success" size="small" effect="plain">{{ t('cashFlow.recordedThisMonth') }}</el-tag>
            <el-tag v-else type="warning" size="small" effect="plain">{{ t('cashFlow.pending') }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column :label="t('common.actions')" width="90" align="center">
          <template #default="{ row }">
            <el-button size="small" link :icon="Edit" @click="openEstateValueDialog(row)">
              {{ t('cashFlow.record') }}
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <FormDialog
      v-model="estateValueDialogVisible"
      :title="t('cashFlow.recordEstateTitle')"
      :loading="estateValueSubmitting"
      width="480px"
      @submit="submitEstateValue"
    >
      <el-form ref="estateValueFormRef" :model="estateValueForm" :rules="estateValueRules" label-width="120px">
        <el-form-item :label="t('cashFlow.colEstate')">
          <span>{{ estateValueForm.estate_name }}</span>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldMonth')">
          <span>{{ store.selectedMonth }}</span>
        </el-form-item>
        <el-form-item :label="t('cashFlow.colMarketValue')" prop="market_value">
          <el-input-number
            v-model="estateValueForm.market_value"
            :precision="2"
            :min="0"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="journalDialogVisible"
      :title="formMode === 'create' ? t('cashFlow.addJournal') : t('cashFlow.editJournal')"
      :loading="submitting"
      width="640px"
      @submit="submitJournal"
    >
      <el-form ref="formRef" :model="formData" :rules="formRules" label-width="100px">
        <el-form-item :label="t('cashFlow.colDate')" prop="spend_date">
          <el-date-picker
            v-model="formDateValue"
            type="date"
            :placeholder="t('cashFlow.selectDate')"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldPaymentSource')" prop="spend_way_type">
          <el-radio-group v-model="formData.spend_way_type" @change="onSpendWayTypeChange">
            <el-radio value="account">{{ t('cashFlow.colAccount') }}</el-radio>
            <el-radio value="credit_card">{{ t('cashFlow.creditCard') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldAccountCard')" prop="spend_way">
          <el-select v-model="formData.spend_way" :placeholder="t('cashFlow.select')" filterable style="width: 100%">
            <el-option-group
              v-for="group in activeSpendWayGroups"
              :key="group.label"
              :label="translateGroupLabel(group.label)"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldMainCategory')" prop="action_main">
          <el-select
            v-model="formData.action_main"
            :placeholder="t('cashFlow.selectMainCategory')"
            filterable
            style="width: 100%"
            @change="onActionMainChange"
          >
            <el-option-group
              v-for="(group, idx) in mainSelectionGroups"
              :key="`${group.label}-${idx}`"
              :label="translateGroupLabel(group.label)"
            >
              <el-option
                v-for="opt in group.options"
                :key="opt.value"
                :label="opt.label"
                :value="opt.value"
                :data-type="group.label"
              />
            </el-option-group>
          </el-select>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldSubCategory')">
          <el-select
            v-model="formData.action_sub"
            :placeholder="t('noteHints.optional')"
            filterable
            clearable
            style="width: 100%"
            :disabled="!formData.action_main"
            @change="onActionSubChange"
          >
            <template
              v-for="(group, idx) in subSelectionGroups"
              :key="`${group.label}-${idx}`"
            >
              <template v-if="group.label === 'sub'">
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </template>
              <el-option-group v-else :label="translateGroupLabel(group.label)">
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                  :data-type="group.label"
                />
              </el-option-group>
            </template>
          </el-select>
        </el-form-item>
        <el-form-item :label="t('cashFlow.colAmount')" prop="spending">
          <el-input-number
            v-model="formData.spending"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
            :disabled="isLoanRepayment"
          />
          <p class="text-xs text-on-surface-variant mt-1">
            {{ isLoanRepayment ? t('cashFlow.loanAmountAutoHint') : t('cashFlow.amountHint') }}
          </p>
        </el-form-item>
        <el-form-item :label="t('cashFlow.fieldInvoice')">
          <el-input v-model="formData.invoice_number" :placeholder="t('noteHints.optional')" />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input
            v-model="formData.note"
            type="textarea"
            :rows="2"
            :placeholder="notePlaceholder"
          />
        </el-form-item>

        <template v-if="shouldShowAssetSync && syncAssetType">
          <el-divider />
          <el-alert
            type="info"
            :closable="false"
            show-icon
            :title="t('cashFlow.syncAssetTitle')"
            :description="t('cashFlow.syncAssetDesc')"
            class="mb-4"
          />
          <!-- Holding picker for stock/insurance/estate. Loan has no separate
               picker — the loan is the journal's sub-category (action_sub). -->
          <el-form-item v-if="syncAssetType !== 'loan'" :label="syncHoldingLabel">
            <el-select
              v-model="syncHoldingId"
              :placeholder="t('cashFlow.selectHolding', { label: syncHoldingLabel })"
              filterable
              style="width: 100%"
              :disabled="currentSyncSelectionGroups.length === 0"
            >
              <el-option-group
                v-for="group in currentSyncSelectionGroups"
                :key="group.label"
                :label="group.label"
              >
                <el-option
                  v-for="opt in group.options"
                  :key="opt.value"
                  :label="opt.label"
                  :value="opt.value"
                />
              </el-option-group>
            </el-select>
            <p
              v-if="currentSyncSelectionGroups.length === 0"
              class="text-xs text-on-surface-variant mt-1"
            >
              {{ syncHoldingEmptyHint }}
            </p>
          </el-form-item>
          <StockDetailFormFields
            v-if="syncAssetType === 'stock'"
            v-model="syncStockDetail"
            mode="cashflow-sync"
            :allowed-types="dividendAllowedTypes"
          />
          <InsuranceDetailFormFields
            v-else-if="syncAssetType === 'insurance'"
            v-model="syncInsuranceDetail"
            mode="cashflow-sync"
          />
          <EstateDetailFormFields
            v-else-if="syncAssetType === 'estate'"
            v-model="syncEstateDetail"
            mode="cashflow-sync"
          />
          <LoanDetailFormFields
            v-else-if="syncAssetType === 'loan'"
            v-model="syncLoanDetail"
            mode="cashflow-sync"
          />
        </template>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus, Edit, Delete, TrendCharts, Wallet, House, Refresh } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import BarChart from '@/components/charts/BarChart.vue'
import DonutChart from '@/components/charts/DonutChart.vue'
import StockDetailFormFields, {
  type StockDetailFormState,
} from '@/components/forms/StockDetailFormFields.vue'
import InsuranceDetailFormFields, {
  type InsuranceDetailFormState,
} from '@/components/forms/InsuranceDetailFormFields.vue'
import EstateDetailFormFields, {
  type EstateDetailFormState,
} from '@/components/forms/EstateDetailFormFields.vue'
import LoanDetailFormFields, {
  type LoanDetailFormState,
} from '@/components/forms/LoanDetailFormFields.vue'
import { useDateStringModel } from '@/composables/useDateStringModel'
import { useMonthDatePicker } from '@/composables/useMonthDatePicker'
import { formatYyyymmddDisplay, todayYyyymmdd } from '@/utils/dateFormat'
import { isUncategorized, normType } from '@/utils/journalTypes'
import { useCashFlowStore } from '@/stores/cashFlow'
import {
  createJournal,
  createJournalWithStockTransaction,
  createJournalWithInsuranceTransaction,
  createJournalWithEstateTransaction,
  createJournalWithLoanTransaction,
  updateJournal,
  updateJournalWithStockTransaction,
  updateJournalWithInsuranceTransaction,
  updateJournalWithEstateTransaction,
  updateJournalWithLoanTransaction,
  deleteJournal,
  settleMonth,
  uploadStockPrices,
  upsertInsuranceValue,
  upsertEstateValue,
} from '@/api/cashFlow'
import {
  getAccountSelections,
  getCodeSelections,
  getCreditCardSelections,
  getEstateSelections,
  getInsuranceSelections,
  getLoanSelections,
  getOtherAssetTypeSelections,
  getStockSelections,
} from '@/api/utilities'
import { getCodesWithSub } from '@/api/setting'
import {
  FINANCIAL_BEHAVIORS,
  getFinancialBehaviorLabel,
} from '@/constants/financialBehavior'
import { getNotePlaceholder } from '@/constants/noteHints'
import { translateGroupLabel } from '@/constants/selectionLabels'
import type { CodeDataWithSub, Journal, JournalCreate, SelectionGroup } from '@/types/models'

const store = useCashFlowStore()
const route = useRoute()
const { t } = useI18n()

// Deep link from the dashboard cleanup banner: ?month=YYYYMM&uncategorized=1
// jumps straight to that month with the uncategorized filter on. Applied in
// setup (not onMounted) so useMonthDatePicker below initializes its picker
// model from the deep-linked month.
const deepLinkMonth = typeof route.query.month === 'string' ? route.query.month : ''
if (/^\d{6}$/.test(deepLinkMonth)) store.selectedMonth = deepLinkMonth

// YYYYMMDD → YYYY-MM-DD for display.
const formatDate = formatYyyymmddDisplay

const { selectedMonthDate } = useMonthDatePicker({
  current: () => store.selectedMonth,
  onChange: (month) => {
    store.selectedMonth = month
    store.fetchJournals()
  },
})

// ─── Uncategorized journals (legacy 'undefined'/'No'/'' rows) ───────────────
const showUncategorizedOnly = ref(false)

const uncategorizedCount = computed(
  () => store.journals.filter((j) => isUncategorized(j.action_main_type)).length,
)

// Falls back to the full list when nothing is uncategorized, so a stale
// toggle (or a deep link into an already-clean month) can't blank the table.
const displayedJournals = computed(() =>
  showUncategorizedOnly.value && uncategorizedCount.value > 0
    ? store.journals.filter((j) => isUncategorized(j.action_main_type))
    : store.journals,
)

// When the last uncategorized row of the month gets classified, drop the
// filter so the table doesn't strand the user on an empty list.
watch(uncategorizedCount, (count) => {
  if (count === 0) showUncategorizedOnly.value = false
})

const totalIncome = computed(() =>
  store.journals
    .filter((j) => j.spending > 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const totalExpense = computed(() =>
  store.journals
    .filter((j) => j.spending < 0)
    .reduce((sum, j) => sum + j.spending, 0),
)

const netTotal = computed(() => totalIncome.value + totalExpense.value)

// ─── Analytics tabs ────────────────────────────────────────────────────────
type ChartTab = 'budget' | 'expenditureRatio' | 'investRatio' | 'liability'
const activeChartTab = ref<ChartTab>('budget')
const loadedTabs = ref<Set<ChartTab>>(new Set())

async function loadChartTab(tab: ChartTab) {
  if (tab === 'budget') await store.fetchExpenditureBudget()
  else if (tab === 'expenditureRatio') await store.fetchExpenditureRatio()
  else if (tab === 'investRatio') await store.fetchInvestRatio()
  else if (tab === 'liability') await store.fetchLiability()
  loadedTabs.value.add(tab)
}

watch(activeChartTab, (tab) => {
  if (!loadedTabs.value.has(tab)) void loadChartTab(tab)
})

watch(
  () => store.selectedMonth,
  () => {
    loadedTabs.value.clear()
    void loadChartTab(activeChartTab.value)
  },
)

const budgetChart = computed(() => {
  const rows = store.expenditureBudget?.rows ?? []
  return {
    xData: rows.map((r) => r.action_main_type),
    series: [
      { name: t('cashFlow.seriesBudget'), data: rows.map((r) => r.expected) },
      { name: t('cashFlow.seriesActual'), data: rows.map((r) => Math.abs(r.actual)) },
    ],
  }
})

// ─── Selection caches ──────────────────────────────────────────────────────
const accountGroups = ref<SelectionGroup[]>([])
const creditCardGroups = ref<SelectionGroup[]>([])
const loanGroups = ref<SelectionGroup[]>([])
const insuranceGroups = ref<SelectionGroup[]>([])
const codeGroups = ref<SelectionGroup[]>([])
const subCodeGroups = ref<SelectionGroup[]>([])
const otherAssetDbTypes = ref<Set<string>>(new Set())

// Maps Other_Asset.asset_type (DB-driven) → the capitalized form historically
// stored in Journal.action_sub plus the matching detail table. Kept inline
// rather than in a constants file: this is dispatch glue, not domain data.
const OTHER_ASSET_DISPATCH: Record<
  string,
  { subKey: string; subTable: string; labelKey: string }
> = {
  stock:     { subKey: 'Stock',     subTable: 'Stock_Detail',     labelKey: 'cashFlow.assetStock' },
  insurance: { subKey: 'Insurance', subTable: 'Insurance_Journal', labelKey: 'cashFlow.assetInsurance' },
  estate:    { subKey: 'Estate',    subTable: 'Estate_Journal',   labelKey: 'cashFlow.assetEstate' },
}
// Composite endpoints exist for all three asset types (CFL-A01). Filter
// narrows the sub dropdown to what we can actually round-trip atomically.
const SUPPORTED_SYNC_ASSET_TYPES: readonly string[] = ['stock', 'insurance', 'estate']
const OTHER_ASSET_SUB_TABLES = new Set(
  Object.values(OTHER_ASSET_DISPATCH).map((m) => m.subTable),
)

const financialBehaviorGroup = computed<SelectionGroup>(() => ({
  label: 'FinancialBehavior',
  options: FINANCIAL_BEHAVIORS.map((b) => ({ value: b.key, label: t(b.labelKey) })),
}))

const mainSelectionGroups = computed<SelectionGroup[]>(() => [
  ...codeGroups.value,
  financialBehaviorGroup.value,
])

const otherAssetSubGroup = computed<SelectionGroup | null>(() => {
  const options = Object.entries(OTHER_ASSET_DISPATCH)
    .filter(([dbType]) => otherAssetDbTypes.value.has(dbType))
    .filter(([dbType]) => SUPPORTED_SYNC_ASSET_TYPES.includes(dbType))
    .map(([, m]) => ({ value: m.subKey, label: t(m.labelKey) }))
  if (options.length === 0) return null
  return { label: 'Other_Asset', options }
})

// Dividend income (被動收入 / Passive) linked to a stock holding so the 股息 also
// lands in that holding's transaction history + yield. Detected from the chosen
// main category's normalized type (mirrors the backend's passive bucket);
// financial behaviors (Transfer/repayments) are never dividends.
const isDividendContext = computed<boolean>(() => {
  if (FINANCIAL_BEHAVIORS.some((b) => b.key === formData.value.action_main)) return false
  return normType(formData.value.action_main_type) === 'passive'
})

// Stock-only sub-option appended under a Passive category so a dividend can reach
// action_sub_table='Stock_Detail'. (The Transfer→Stock path forces
// action_main_type='Transfer', which would hide the income from the reports.)
const dividendStockSubGroup = computed<SelectionGroup | null>(() => {
  if (!otherAssetDbTypes.value.has('stock')) return null
  const m = OTHER_ASSET_DISPATCH.stock
  return { label: 'Other_Asset', options: [{ value: m.subKey, label: t(m.labelKey) }] }
})

// Lock the synced detail to a cash dividend in the dividend flow (the only
// dividend type in scope); the buy/sell path passes undefined (all four types).
const dividendAllowedTypes = computed<('buy' | 'sell' | 'stock' | 'cash')[] | undefined>(() =>
  isDividendContext.value ? ['cash'] : undefined,
)

const subSelectionGroups = computed<SelectionGroup[]>(() => {
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === formData.value.action_main)
  if (!behavior) {
    // Passive income → also offer the stock holding so the 股息 can sync to Stock_Detail.
    return isDividendContext.value && dividendStockSubGroup.value
      ? [...subCodeGroups.value, dividendStockSubGroup.value]
      : subCodeGroups.value
  }
  if (behavior.table === 'Account') {
    // Transfer → accounts + Other_Asset (Stock/Insurance/Estate, filtered by
    // what's set up in DB and what the backend can sync atomically).
    return otherAssetSubGroup.value
      ? [...accountGroups.value, otherAssetSubGroup.value]
      : accountGroups.value
  }
  if (behavior.table === 'Credit_Card') return creditCardGroups.value
  if (behavior.table === 'Loan') return loanGroups.value
  if (behavior.table === 'Insurance') return insuranceGroups.value
  return []
})

const notePlaceholder = computed<string>(() => {
  const main = formData.value.action_main
  if (!main) return getNotePlaceholder()
  if (FINANCIAL_BEHAVIORS.some((b) => b.key === main)) {
    return getNotePlaceholder(main)
  }
  const mainName = codeNameMap.value.get(main)
  if (!mainName) return getNotePlaceholder()
  const sub = formData.value.action_sub
  const subName = sub ? codeNameMap.value.get(sub) : undefined
  return getNotePlaceholder(mainName, subName ?? undefined)
})

const activeSpendWayGroups = computed(() =>
  formData.value.spend_way_type === 'credit_card' ? creditCardGroups.value : accountGroups.value,
)

const codeTree = ref<CodeDataWithSub[]>([])

const codeNameMap = computed(() => {
  const map = new Map<string, string>()
  for (const c of codeTree.value) {
    map.set(c.code_id, c.name)
    for (const sub of c.sub_codes ?? []) map.set(sub.code_id, sub.name)
  }
  return map
})

function codeName(id?: string | null): string {
  if (!id) return '-'
  return codeNameMap.value.get(id) ?? id
}

function isCodeTable(table?: string | null): boolean {
  return table === 'Code_Data' || table === 'Code'
}

function actionMainLabel(row: Journal): string {
  if (!row.action_main || row.action_main === 'No') return '-'
  if (isCodeTable(row.action_main_table)) return codeName(row.action_main)
  const behavior = getFinancialBehaviorLabel(row.action_main, row.action_main_table)
  return behavior ?? row.action_main
}

function actionSubLabel(row: Journal): string {
  if (!row.action_sub || row.action_sub === 'No') return '-'
  if (isCodeTable(row.action_sub_table)) return codeName(row.action_sub)
  const table = row.action_sub_table ?? ''
  if (table === 'Account' || table === 'Credit_Card') {
    return spendWayLabelMap.value.get(`${table}:${row.action_sub}`) ?? row.action_sub
  }
  if (table === 'Stock_Detail') return row.action_sub === 'Stock' ? t('cashFlow.assetStock') : row.action_sub
  if (table === 'Insurance_Journal') return t('cashFlow.assetInsurance')
  if (table === 'Estate_Journal') return t('cashFlow.assetEstate')
  return row.action_sub
}

async function loadCodeTree() {
  if (codeTree.value.length === 0) {
    codeTree.value = await getCodesWithSub()
  }
}

const spendWayLabelMap = computed(() => {
  const map = new Map<string, string>()
  const collect = (groups: SelectionGroup[], table: 'Account' | 'Credit_Card') => {
    for (const group of groups) {
      for (const opt of group.options) {
        map.set(`${table}:${opt.value}`, opt.label)
      }
    }
  }
  collect(accountGroups.value, 'Account')
  collect(creditCardGroups.value, 'Credit_Card')
  return map
})

function spendWayLabel(row: Journal): string {
  const key = `${row.spend_way_table}:${row.spend_way}`
  return spendWayLabelMap.value.get(key) ?? row.spend_way
}

async function loadSpendWaySelections() {
  if (accountGroups.value.length === 0) {
    accountGroups.value = await getAccountSelections()
  }
  if (creditCardGroups.value.length === 0) {
    creditCardGroups.value = await getCreditCardSelections()
  }
}

async function loadLoanSelections() {
  if (loanGroups.value.length === 0) {
    try {
      loanGroups.value = await getLoanSelections()
    } catch {
      loanGroups.value = []
    }
  }
}

async function loadInsuranceSelections() {
  if (insuranceGroups.value.length === 0) {
    try {
      insuranceGroups.value = await getInsuranceSelections()
    } catch {
      insuranceGroups.value = []
    }
  }
}

async function loadCodeSelections() {
  if (codeGroups.value.length === 0) {
    codeGroups.value = await getCodeSelections()
  }
}

async function loadSubCodeSelections(parent: string) {
  if (!parent) {
    subCodeGroups.value = []
    return
  }
  try {
    subCodeGroups.value = await getCodeSelections(parent)
  } catch {
    subCodeGroups.value = []
  }
}

// ─── Form state ────────────────────────────────────────────────────────────
type JournalFormState = JournalCreate & { distinct_number?: number; action_sub?: string | null }

function emptyForm(): JournalFormState {
  return {
    vesting_month: store.selectedMonth,
    spend_date: todayYyyymmdd(),
    spend_way: '',
    spend_way_type: 'account',
    spend_way_table: 'Account',
    action_main: '',
    action_main_type: '',
    action_main_table: 'Code_Data',
    action_sub: null,
    action_sub_type: null,
    action_sub_table: null,
    spending: 0,
    invoice_number: null,
    note: null,
  }
}

const journalDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const formData = ref<JournalFormState>(emptyForm())
const formRef = ref<FormInstance>()
const submitting = ref(false)

const formDateValue = useDateStringModel(
  () => formData.value.spend_date,
  (date) => {
    formData.value.spend_date = date ?? ''
  },
)

const formRules = computed<FormRules>(() => ({
  spend_date: [{ required: true, message: t('validation.pickDate'), trigger: 'change' }],
  spend_way: [{ required: true, message: t('validation.pickAccount'), trigger: 'change' }],
  spend_way_type: [{ required: true, message: t('validation.pickPaymentSource'), trigger: 'change' }],
  action_main: [{ required: true, message: t('validation.pickMainCategory'), trigger: 'change' }],
  spending: [{ required: true, message: t('validation.enterAmount'), trigger: 'blur' }],
}))

// ─── Sync-to-asset (Stock / Insurance / Estate) ───────────────────────────
// The user triggers this implicitly by picking an "其他資產" sub-category
// under Transfer (legacy 轉帳→股票 semantics). When triggered, the form
// expands to capture the holding + type, then submits via the matching
// composite endpoint so Journal + <Asset>_Detail land atomically.
type SyncAssetType = 'stock' | 'insurance' | 'estate' | 'loan'

const originalActionSub = ref<string | null>(null) // captured on dialog open
const syncHoldingId = ref('') // selected stock_id / insurance_id / estate_id

// Which composite flow the current sub-category maps to (null = plain journal).
const syncAssetType = computed<SyncAssetType | null>(() => {
  switch (formData.value.action_sub_table) {
    case 'Stock_Detail':
      return 'stock'
    case 'Insurance_Journal':
      return 'insurance'
    case 'Estate_Journal':
      return 'estate'
    case 'Loan':
      // The LoanRepayment behavior sets action_sub_table='Loan' and action_sub
      // to the picked loan_id — the loan is the sub-category, so there is no
      // separate holding picker (unlike stock/insurance/estate).
      return 'loan'
    default:
      return null
  }
})

const stockSelectionGroups = ref<SelectionGroup[]>([])
const estateSelectionGroups = ref<SelectionGroup[]>([])
// Insurance reuses `insuranceGroups` (already loaded for the 保險 main category).

const currentSyncSelectionGroups = computed<SelectionGroup[]>(() => {
  switch (syncAssetType.value) {
    case 'stock':
      return stockSelectionGroups.value
    case 'insurance':
      return insuranceGroups.value
    case 'estate':
      return estateSelectionGroups.value
    default:
      return []
  }
})

const SYNC_HOLDING_LABEL: Record<SyncAssetType, string> = {
  stock: 'cashFlow.holdingStock',
  insurance: 'cashFlow.colInsurance',
  estate: 'cashFlow.colEstate',
  // Loan has no separate holding picker (the loan is the sub-category), so this
  // is never rendered — kept for the Record's exhaustiveness only.
  loan: 'financialBehavior.loanRepayment',
}
const SYNC_HOLDING_EMPTY_HINT: Record<SyncAssetType, string> = {
  stock: 'cashFlow.holdingEmptyStock',
  insurance: 'cashFlow.holdingEmptyInsurance',
  estate: 'cashFlow.holdingEmptyEstate',
  loan: 'financialBehavior.loanRepayment',
}
const syncHoldingLabel = computed(() =>
  syncAssetType.value ? t(SYNC_HOLDING_LABEL[syncAssetType.value]) : '',
)
const syncHoldingEmptyHint = computed(() =>
  syncAssetType.value ? t(SYNC_HOLDING_EMPTY_HINT[syncAssetType.value]) : '',
)

function emptyStockSyncDetail(): StockDetailFormState {
  return {
    stock_id: '',
    excute_type: 'buy',
    excute_amount: 0,
    excute_price: 0,
    excute_date: '',
    account_id: '',
    account_name: '',
    memo: null,
  }
}
const syncStockDetail = ref<StockDetailFormState>(emptyStockSyncDetail())

function emptyInsuranceSyncDetail(): InsuranceDetailFormState {
  return {
    insurance_id: '',
    insurance_excute_type: 'pay',
    excute_price: 0,
    excute_date: '',
    memo: null,
  }
}
const syncInsuranceDetail = ref<InsuranceDetailFormState>(emptyInsuranceSyncDetail())

function emptyEstateSyncDetail(): EstateDetailFormState {
  return {
    estate_id: '',
    estate_excute_type: 'tax',
    excute_price: 0,
    excute_date: '',
    memo: null,
  }
}
const syncEstateDetail = ref<EstateDetailFormState>(emptyEstateSyncDetail())

function emptyLoanSyncDetail(): LoanDetailFormState {
  return { principal: 0, interest: 0 }
}
const syncLoanDetail = ref<LoanDetailFormState>(emptyLoanSyncDetail())

// Noun used in the success toast ("已同步到<noun>明細").
const SYNC_ASSET_NOUN: Record<SyncAssetType, string> = {
  stock: 'cashFlow.assetStock',
  insurance: 'cashFlow.assetInsurance',
  estate: 'cashFlow.assetEstate',
  loan: 'cashFlow.assetLoan',
}

// Composite detail payloads. Each type only carries the user-chosen fields;
// the backend fills excute_price (= journal.spending, sign preserved), date
// and memo from the journal.
function stockDetailBody() {
  return {
    stock_id: syncHoldingId.value,
    excute_type: syncStockDetail.value.excute_type as 'buy' | 'sell' | 'stock' | 'cash',
    excute_amount: Number(syncStockDetail.value.excute_amount ?? 0),
  }
}
function insuranceDetailBody() {
  return {
    insurance_id: syncHoldingId.value,
    insurance_excute_type: syncInsuranceDetail.value.insurance_excute_type as
      | 'pay' | 'cash' | 'return' | 'expect',
  }
}
function estateDetailBody() {
  return {
    estate_id: syncHoldingId.value,
    estate_excute_type: syncEstateDetail.value.estate_excute_type as
      | 'tax' | 'fee' | 'insurance' | 'fix' | 'rent' | 'deposit',
  }
}
// Loan: the loan_id is the picked sub-category (action_sub), not a separate
// holding. principal/interest are positive magnitudes; the backend writes one
// Loan_Journal row per non-zero portion.
function loanDetailBody() {
  return {
    loan_id: formData.value.action_sub ?? '',
    principal: Number(syncLoanDetail.value.principal ?? 0),
    interest: Number(syncLoanDetail.value.interest ?? 0),
  }
}

async function loadStockSelections() {
  if (stockSelectionGroups.value.length > 0) return
  try {
    stockSelectionGroups.value = await getStockSelections()
  } catch {
    stockSelectionGroups.value = []
  }
}

async function loadEstateSelections() {
  if (estateSelectionGroups.value.length > 0) return
  try {
    estateSelectionGroups.value = await getEstateSelections()
  } catch {
    estateSelectionGroups.value = []
  }
}

// Lazy-load the selection list for whichever asset type the sync panel needs.
function loadSyncSelections(type: SyncAssetType) {
  if (type === 'stock') void loadStockSelections()
  else if (type === 'insurance') void loadInsuranceSelections()
  else if (type === 'estate') void loadEstateSelections()
}

async function loadOtherAssetTypes() {
  if (otherAssetDbTypes.value.size > 0) return
  try {
    const groups = await getOtherAssetTypeSelections()
    // Normalize to lowercase: legacy data has mixed casing ("Stock" vs "stock"),
    // dispatch map keys are lowercase for consistency.
    const values = groups[0]?.options.map((o) => o.value.toLowerCase()) ?? []
    otherAssetDbTypes.value = new Set(values)
  } catch {
    otherAssetDbTypes.value = new Set()
  }
}

function resetSyncState() {
  syncHoldingId.value = ''
  syncStockDetail.value = emptyStockSyncDetail()
  syncInsuranceDetail.value = emptyInsuranceSyncDetail()
  syncEstateDetail.value = emptyEstateSyncDetail()
  syncLoanDetail.value = emptyLoanSyncDetail()
}

// Sync panel opens when the user has picked an "其他資產" sub-category (or a loan
// under 繳貸款) and the edit-mode guard allows it. Edit-mode guard: only when the
// original sub was empty — protects existing detail rows from being doubled.
const shouldShowAssetSync = computed<boolean>(() => {
  const table = formData.value.action_sub_table
  const syncable = (table != null && OTHER_ASSET_SUB_TABLES.has(table)) || syncAssetType.value === 'loan'
  if (!syncable) return false
  if (formMode.value === 'create') return true
  return !originalActionSub.value
})

// Lazy-load the holding dropdown whenever the sync panel is visible and the
// asset type changes (e.g. switching the sub-category from 股票 to 保險). Reset
// the picked holding so a stale id from another type can't leak through.
watch([shouldShowAssetSync, syncAssetType], ([visible, type], [, prevType]) => {
  if (type !== prevType) syncHoldingId.value = ''
  if (visible && type) loadSyncSelections(type)
})

// In a dividend context lock the synced detail to a cash dividend (the only
// dividend type in scope); reset to the buy default when leaving it so a later
// buy/sell isn't stuck on 'cash'.
watch(isDividendContext, (isDiv) => {
  syncStockDetail.value = {
    ...syncStockDetail.value,
    excute_type: isDiv ? 'cash' : 'buy',
    excute_amount: 0,
  }
})

// A loan repayment's total cash outflow is the sum of its principal + interest,
// so the main 金額 field is derived (and shown read-only) from the split.
const isLoanRepayment = computed(() => syncAssetType.value === 'loan')
watch(
  [isLoanRepayment, () => syncLoanDetail.value.principal, () => syncLoanDetail.value.interest],
  ([isLoan, principal, interest]) => {
    if (isLoan) {
      formData.value.spending = -(Number(principal ?? 0) + Number(interest ?? 0))
    }
  },
)

function findCodeType(groups: SelectionGroup[], value: string): string {
  for (const group of groups) {
    if (group.options.some((opt) => opt.value === value)) return group.label
  }
  return ''
}

function onSpendWayTypeChange(value: string | number | boolean | undefined) {
  const v = String(value)
  formData.value.spend_way = ''
  formData.value.spend_way_table = v === 'credit_card' ? 'Credit_Card' : 'Account'
}

async function onActionMainChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  formData.value.action_sub = null
  formData.value.action_sub_type = null
  formData.value.action_sub_table = null
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === v)
  if (behavior) {
    formData.value.action_main_type = behavior.key
    formData.value.action_main_table = behavior.table
    subCodeGroups.value = []
    if (behavior.table === 'Loan') await loadLoanSelections()
    if (behavior.table === 'Insurance') await loadInsuranceSelections()
  } else {
    formData.value.action_main_type = findCodeType(codeGroups.value, v)
    formData.value.action_main_table = 'Code_Data'
    await loadSubCodeSelections(v)
  }
}

function onActionSubChange(value: string | number | boolean | undefined) {
  const v = value ? String(value) : ''
  if (!v) {
    formData.value.action_sub = null
    formData.value.action_sub_type = null
    formData.value.action_sub_table = null
    return
  }
  formData.value.action_sub = v
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === formData.value.action_main)
  // Transfer → Other_Asset (Stock / Insurance / Estate): dispatch matches the
  // legacy account-book-view convention so existing rows keep rendering.
  const otherAssetEntry = Object.values(OTHER_ASSET_DISPATCH).find((m) => m.subKey === v)
  if (behavior?.table === 'Account' && otherAssetEntry) {
    formData.value.action_sub_table = otherAssetEntry.subTable
    formData.value.action_sub_type = 'Asset'
    return
  }
  // Passive income → Stock: same Stock_Detail sync as Transfer→Stock, but the
  // journal stays Passive (action_main_type untouched) so the income statement
  // still counts it as 孳息. action_sub keeps the literal 'Stock' set above, for
  // re-edit idempotency (shouldShowAssetSync) and the correct table-row label.
  if (isDividendContext.value && otherAssetEntry?.subTable === 'Stock_Detail') {
    formData.value.action_sub_table = 'Stock_Detail'
    formData.value.action_sub_type = 'Asset'
    return
  }
  if (behavior) {
    formData.value.action_sub_table = behavior.table
    formData.value.action_sub_type = findCodeType(subSelectionGroups.value, v)
  } else {
    formData.value.action_sub_table = 'Code_Data'
    formData.value.action_sub_type = findCodeType(subCodeGroups.value, v)
  }
}

async function openCreateJournal() {
  formMode.value = 'create'
  formData.value = emptyForm()
  subCodeGroups.value = []
  originalActionSub.value = null
  resetSyncState()
  journalDialogVisible.value = true
  await Promise.all([
    loadSpendWaySelections(),
    loadCodeSelections(),
    loadOtherAssetTypes(),
  ])
}

async function editJournal(row: Journal) {
  formMode.value = 'edit'
  formData.value = {
    distinct_number: row.distinct_number,
    vesting_month: row.vesting_month,
    spend_date: row.spend_date,
    spend_way: row.spend_way,
    spend_way_type: row.spend_way_type,
    spend_way_table: row.spend_way_table,
    action_main: row.action_main,
    action_main_type: row.action_main_type,
    action_main_table: row.action_main_table,
    action_sub: row.action_sub ?? null,
    action_sub_type: row.action_sub_type ?? null,
    action_sub_table: row.action_sub_table ?? null,
    spending: row.spending,
    invoice_number: row.invoice_number ?? null,
    note: row.note ?? null,
  }
  originalActionSub.value = row.action_sub ?? null
  resetSyncState()
  journalDialogVisible.value = true
  await Promise.all([
    loadSpendWaySelections(),
    loadCodeSelections(),
    loadOtherAssetTypes(),
  ])
  const behavior = FINANCIAL_BEHAVIORS.find((b) => b.key === row.action_main)
  if (behavior) {
    if (behavior.table === 'Loan') await loadLoanSelections()
    if (behavior.table === 'Insurance') await loadInsuranceSelections()
  } else if (row.action_main) {
    await loadSubCodeSelections(row.action_main)
  }
}

async function submitJournal() {
  if (!formRef.value) return
  const valid = await formRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    const payload: JournalCreate = {
      vesting_month: formData.value.vesting_month,
      spend_date: formData.value.spend_date,
      spend_way: formData.value.spend_way,
      spend_way_type: formData.value.spend_way_type,
      spend_way_table: formData.value.spend_way_table,
      action_main: formData.value.action_main,
      action_main_type: formData.value.action_main_type,
      action_main_table: formData.value.action_main_table,
      action_sub: formData.value.action_sub ?? null,
      action_sub_type: formData.value.action_sub_type ?? null,
      action_sub_table: formData.value.action_sub_table ?? null,
      spending: Number(formData.value.spending ?? 0),
      invoice_number: formData.value.invoice_number || null,
      note: formData.value.note || null,
    }
    const syncType = shouldShowAssetSync.value ? syncAssetType.value : null
    // Loan has no separate holding picker (the loan is action_sub); the others
    // require a picked holding.
    if (syncType && syncType !== 'loan' && !syncHoldingId.value) {
      ElMessage.error(t('cashFlow.selectHolding', { label: syncHoldingLabel.value }))
      return
    }
    // Dividend income is an inflow: a non-positive amount would shrink 孳息 income
    // (the income statement reads the signed amount). Mirror the backend guard.
    if (syncType === 'stock' && isDividendContext.value && payload.spending <= 0) {
      ElMessage.error(t('cashFlow.dividendMustBePositive'))
      return
    }
    // Loan repayment: principal + interest must be a positive total (matches the
    // backend guard; the main 金額 is the derived −total).
    if (syncType === 'loan') {
      const total = Number(syncLoanDetail.value.principal ?? 0) + Number(syncLoanDetail.value.interest ?? 0)
      if (total <= 0) {
        ElMessage.error(t('cashFlow.loanSplitRequired'))
        return
      }
    }

    if (formMode.value === 'create') {
      switch (syncType) {
        case 'stock':
          await createJournalWithStockTransaction({ journal: payload, stock_detail: stockDetailBody() })
          break
        case 'insurance':
          await createJournalWithInsuranceTransaction({ journal: payload, insurance_detail: insuranceDetailBody() })
          break
        case 'estate':
          await createJournalWithEstateTransaction({ journal: payload, estate_detail: estateDetailBody() })
          break
        case 'loan':
          await createJournalWithLoanTransaction({ journal: payload, loan_detail: loanDetailBody() })
          break
        default:
          await createJournal(payload)
      }
      ElMessage.success(syncType ? t('cashFlow.createSyncedSuccess', { noun: t(SYNC_ASSET_NOUN[syncType]) }) : t('toast.addSuccess'))
    } else if (formData.value.distinct_number !== undefined) {
      const id = formData.value.distinct_number
      switch (syncType) {
        case 'stock':
          await updateJournalWithStockTransaction(id, { journal: payload, stock_detail: stockDetailBody() })
          break
        case 'insurance':
          await updateJournalWithInsuranceTransaction(id, { journal: payload, insurance_detail: insuranceDetailBody() })
          break
        case 'estate':
          await updateJournalWithEstateTransaction(id, { journal: payload, estate_detail: estateDetailBody() })
          break
        case 'loan':
          await updateJournalWithLoanTransaction(id, { journal: payload, loan_detail: loanDetailBody() })
          break
        default:
          await updateJournal(id, payload)
      }
      ElMessage.success(syncType ? t('cashFlow.updateSyncedSuccess', { noun: t(SYNC_ASSET_NOUN[syncType]) }) : t('toast.updateSuccess'))
    }
    journalDialogVisible.value = false
    await store.fetchJournals()
  } finally {
    submitting.value = false
  }
}

async function handleDeleteJournal(id: number) {
  await deleteJournal(id)
  ElMessage.success(t('toast.deleted'))
  await store.fetchJournals()
}

// ─── Settle ────────────────────────────────────────────────────────────────
const settling = ref(false)

async function confirmSettle() {
  try {
    await ElMessageBox.confirm(
      t('cashFlow.settleConfirm', { month: store.selectedMonth }),
      t('cashFlow.settleConfirmTitle'),
      { type: 'warning', confirmButtonText: t('cashFlow.execute'), cancelButtonText: t('common.cancel') },
    )
  } catch {
    return
  }
  settling.value = true
  try {
    const result = await settleMonth(store.selectedMonth)
    ElMessage.success(t('cashFlow.settleDone', { account: result.account_rows, creditCard: result.credit_card_rows }))
    await store.fetchJournals()
    loadedTabs.value.clear()
    void loadChartTab(activeChartTab.value)
  } finally {
    settling.value = false
  }
}

// ─── Stock prices ──────────────────────────────────────────────────────────
const stockPriceSnapshotVisible = ref(false)
const stockPriceDialogVisible = ref(false)

function openStockPriceSnapshot() {
  stockPriceSnapshotVisible.value = true
}
const stockPriceSubmitting = ref(false)
const stockPriceFormRef = ref<FormInstance>()

interface StockPriceFormState {
  stock_code: string
  fetch_date: string
  open_price: number
  highest_price: number
  lowest_price: number
  close_price: number
  trigger_yfinance: boolean
}

function emptyStockPriceForm(): StockPriceFormState {
  return {
    stock_code: '',
    fetch_date: todayYyyymmdd(),
    open_price: 0,
    highest_price: 0,
    lowest_price: 0,
    close_price: 0,
    trigger_yfinance: false,
  }
}

const stockPriceForm = ref<StockPriceFormState>(emptyStockPriceForm())

const stockPriceFormDate = useDateStringModel(
  () => stockPriceForm.value.fetch_date,
  (date) => {
    stockPriceForm.value.fetch_date = date ?? ''
  },
)

const stockPriceRules = computed<FormRules>(() => ({
  stock_code: [{ required: true, message: t('validation.enterCode'), trigger: 'blur' }],
  fetch_date: [{ required: true, message: t('validation.pickDate'), trigger: 'change' }],
  open_price: [{ required: true, message: t('validation.enterOpenPrice'), trigger: 'blur' }],
  highest_price: [{ required: true, message: t('validation.enterHighPrice'), trigger: 'blur' }],
  lowest_price: [{ required: true, message: t('validation.enterLowPrice'), trigger: 'blur' }],
  close_price: [{ required: true, message: t('validation.enterClosePrice'), trigger: 'blur' }],
}))

function openStockPriceDialog(prefillCode?: string) {
  stockPriceForm.value = {
    ...emptyStockPriceForm(),
    ...(prefillCode ? { stock_code: prefillCode } : {}),
  }
  stockPriceDialogVisible.value = true
}

async function submitStockPrice() {
  if (!stockPriceFormRef.value) return
  const valid = await stockPriceFormRef.value.validate().catch(() => false)
  if (!valid) return
  stockPriceSubmitting.value = true
  try {
    await uploadStockPrices({ ...stockPriceForm.value })
    ElMessage.success(t('cashFlow.stockPriceAdded'))
    stockPriceDialogVisible.value = false
    await store.fetchStockPrices()
  } finally {
    stockPriceSubmitting.value = false
  }
}

watch(
  () => store.selectedMonth,
  () => {
    void store.fetchStockPrices()
    void store.fetchInsuranceValues()
    void store.fetchEstateValues()
  },
)

// ─── Insurance surrender values (解約金) ─────────────────────────────────────
const insuranceSnapshotVisible = ref(false)
const insuranceValueDialogVisible = ref(false)
const insuranceValueSubmitting = ref(false)
const insuranceValueFormRef = ref<FormInstance>()

interface InsuranceValueFormState {
  insurance_id: string
  insurance_name: string
  surrender_value: number
}

const insuranceValueForm = ref<InsuranceValueFormState>({
  insurance_id: '',
  insurance_name: '',
  surrender_value: 0,
})

const insuranceValueRules = computed<FormRules>(() => ({
  surrender_value: [{ required: true, message: t('validation.enterSurrenderValue'), trigger: 'blur' }],
}))

function openInsuranceSnapshot() {
  insuranceSnapshotVisible.value = true
  void store.fetchInsuranceValues()
}

function openInsuranceValueDialog(row: {
  insurance_id: string
  insurance_name: string
  surrender_value: number | null
}) {
  insuranceValueForm.value = {
    insurance_id: row.insurance_id,
    insurance_name: row.insurance_name,
    surrender_value: row.surrender_value ?? 0,
  }
  insuranceValueDialogVisible.value = true
}

async function submitInsuranceValue() {
  if (!insuranceValueFormRef.value) return
  const valid = await insuranceValueFormRef.value.validate().catch(() => false)
  if (!valid) return
  insuranceValueSubmitting.value = true
  try {
    await upsertInsuranceValue({
      insurance_id: insuranceValueForm.value.insurance_id,
      vesting_month: store.selectedMonth,
      surrender_value: insuranceValueForm.value.surrender_value,
    })
    ElMessage.success(t('cashFlow.surrenderRecorded'))
    insuranceValueDialogVisible.value = false
    await store.fetchInsuranceValues()
  } finally {
    insuranceValueSubmitting.value = false
  }
}

// ─── Estate market values (房產估值) ─────────────────────────────────────────
const estateSnapshotVisible = ref(false)
const estateValueDialogVisible = ref(false)
const estateValueSubmitting = ref(false)
const estateValueFormRef = ref<FormInstance>()

interface EstateValueFormState {
  estate_id: string
  estate_name: string
  market_value: number
}

const estateValueForm = ref<EstateValueFormState>({
  estate_id: '',
  estate_name: '',
  market_value: 0,
})

const estateValueRules = computed<FormRules>(() => ({
  market_value: [{ required: true, message: t('validation.enterMarketValue'), trigger: 'blur' }],
}))

const refreshingIndex = ref(false)

function openEstateSnapshot() {
  estateSnapshotVisible.value = true
  void store.fetchEstateValues()
  void store.fetchEstateSuggestions()
}

function suggestedValueFor(estateId: string): number | null {
  const s = store.estateSuggestions.find((x) => x.estate_id === estateId)
  return s ? s.suggested_market_value : null
}

function applySuggestion(row: {
  estate_id: string
  estate_name: string
  market_value: number | null
}) {
  openEstateValueDialog({ ...row, market_value: suggestedValueFor(row.estate_id) ?? row.market_value })
}

async function refreshIndex() {
  refreshingIndex.value = true
  try {
    const res = await store.refreshEstateIndex()
    if (res.ok) ElMessage.success(t('cashFlow.indexUpdated', { count: res.upserted }))
    else ElMessage.warning(t('cashFlow.indexUpdateFailed'))
  } finally {
    refreshingIndex.value = false
  }
}

function openEstateValueDialog(row: {
  estate_id: string
  estate_name: string
  market_value: number | null
}) {
  estateValueForm.value = {
    estate_id: row.estate_id,
    estate_name: row.estate_name,
    market_value: row.market_value ?? 0,
  }
  estateValueDialogVisible.value = true
}

async function submitEstateValue() {
  if (!estateValueFormRef.value) return
  const valid = await estateValueFormRef.value.validate().catch(() => false)
  if (!valid) return
  estateValueSubmitting.value = true
  try {
    await upsertEstateValue({
      estate_id: estateValueForm.value.estate_id,
      vesting_month: store.selectedMonth,
      market_value: estateValueForm.value.market_value,
    })
    ElMessage.success(t('cashFlow.estateValueRecorded'))
    estateValueDialogVisible.value = false
    await store.fetchEstateValues()
  } finally {
    estateValueSubmitting.value = false
  }
}

onMounted(() => {
  if (route.query.uncategorized === '1') showUncategorizedOnly.value = true
  store.fetchJournals()
  store.fetchStockPrices()
  store.fetchInsuranceValues()
  store.fetchEstateValues()
  void loadSpendWaySelections()
  void loadCodeTree()
  void loadChartTab(activeChartTab.value)
})
</script>
