<template>
  <div class="flex flex-col gap-6">
    <PageHeader :title="t('settingMenu.title')" :subtitle="t('settingMenu.subtitle')" />

    <el-tabs v-model="activeTab" class="settings-tabs">
      <el-tab-pane :label="t('settingMenu.tabAccounts')" name="accounts">
        <DataListCard :title="t('settingMenu.accountListTitle')">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateAccount">
              {{ t('settingMenu.addAccount') }}
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.accounts"
              v-loading="store.accountsLoading"
              row-key="id"
              stripe
              :empty-text="t('settingMenu.noAccounts')"
            >
              <el-table-column prop="account_id" :label="t('settingMenu.accountId')" min-width="140" />
              <el-table-column prop="name" :label="t('common.name')" min-width="160" />
              <el-table-column prop="account_type" :label="t('common.type')" min-width="100" />
              <el-table-column prop="fx_code" :label="t('settingMenu.fxCode')" width="80" />
              <el-table-column :label="t('common.enable')" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="discount" :label="t('settingMenu.discount')" width="80" />
              <el-table-column prop="owner" :label="t('settingMenu.owner')" min-width="120">
                <template #default="{ row }">{{ row.owner ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="account_index" :label="t('settingMenu.sortIndex')" width="80" />
              <el-table-column :label="t('common.actions')" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditAccount(row)" @delete="handleDeleteAccount(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane :label="t('settingMenu.tabCodes')" name="codes">
        <DataListCard :title="t('settingMenu.codeListTitle')">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateCode">
              {{ t('settingMenu.addMainCode') }}
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.codesWithSub"
              v-loading="store.codesLoading"
              row-key="code_id"
              stripe
              :empty-text="t('settingMenu.noMainCodes')"
            >
              <el-table-column type="expand">
                <template #default="{ row }">
                  <div class="px-6 py-4 flex flex-col gap-3">
                    <SectionHeader
                      :title="t('settingMenu.subCodesOf', { id: row.code_id })"
                      :action-text="t('settingMenu.addSubCode')"
                      @action="openCreateSubCode(row)"
                    />
                    <el-table
                      :data="row.sub_codes ?? []"
                      :empty-text="t('settingMenu.noSubCodes')"
                      size="small"
                    >
                      <el-table-column prop="code_id" :label="t('settingMenu.subCodeId')" min-width="120" />
                      <el-table-column prop="name" :label="t('common.name')" min-width="160" />
                      <el-table-column :label="t('common.enable')" width="80">
                        <template #default="{ row: sub }">
                          <StatusBadge :value="sub.in_use" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="code_index" :label="t('settingMenu.sortIndex')" width="80" />
                      <el-table-column :label="t('common.actions')" width="160" fixed="right">
                        <template #default="{ row: sub }">
                          <RowActions
                            variant="link"
                            @edit="openEditSubCode(row, sub)"
                            @delete="handleDeleteSubCode(sub)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </div>
                </template>
              </el-table-column>
              <el-table-column prop="code_id" :label="t('settingMenu.codeId')" min-width="120" />
              <el-table-column prop="name" :label="t('common.name')" min-width="160" />
              <el-table-column prop="code_type" :label="t('common.type')" min-width="110" />
              <el-table-column :label="t('settingMenu.annualEvent')" width="100">
                <template #default="{ row }">
                  <el-tag v-if="row.is_annual_event" size="small" type="warning">{{ t('settingMenu.eventTag') }}</el-tag>
                  <span v-else class="text-on-surface-muted">—</span>
                </template>
              </el-table-column>
              <el-table-column :label="t('common.enable')" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="code_index" :label="t('settingMenu.sortIndex')" width="80" />
              <el-table-column :label="t('common.actions')" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditCode(row)" @delete="handleDeleteCode(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane :label="t('settingMenu.tabCreditCards')" name="credit-cards">
        <DataListCard :title="t('settingMenu.creditCardListTitle')">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateCreditCard">
              {{ t('settingMenu.addCreditCard') }}
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.creditCards"
              v-loading="store.creditCardsLoading"
              row-key="credit_card_id"
              stripe
              :empty-text="t('settingMenu.noCreditCards')"
            >
              <el-table-column prop="credit_card_id" :label="t('settingMenu.cardId')" min-width="140" />
              <el-table-column prop="card_name" :label="t('settingMenu.cardName')" min-width="160" />
              <el-table-column prop="card_no" :label="t('settingMenu.cardNo')" min-width="160">
                <template #default="{ row }">{{ row.card_no ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="last_day" :label="t('settingMenu.lastDay')" width="90">
                <template #default="{ row }">{{ row.last_day ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="charge_day" :label="t('settingMenu.chargeDay')" width="90">
                <template #default="{ row }">{{ row.charge_day ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="limit_date" :label="t('settingMenu.limitDate')" width="90">
                <template #default="{ row }">{{ row.limit_date ?? '—' }}</template>
              </el-table-column>
              <el-table-column prop="fx_code" :label="t('settingMenu.fxCode')" width="80" />
              <el-table-column :label="t('common.enable')" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column prop="credit_card_index" :label="t('settingMenu.sortIndex')" width="80" />
              <el-table-column :label="t('common.actions')" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditCreditCard(row)" @delete="handleDeleteCreditCard(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>

      <el-tab-pane :label="t('settingMenu.tabStockCategories')" name="stock-categories">
        <DataListCard :title="t('settingMenu.stockCategoryListTitle')">
          <template #menu>
            <el-button type="primary" :icon="PlusIcon" @click="openCreateStockCategory">
              {{ t('settingMenu.addStockCategory') }}
            </el-button>
          </template>

          <div class="p-4">
            <el-table
              :data="store.stockCategories"
              v-loading="store.stockCategoriesLoading"
              row-key="category_id"
              stripe
              :empty-text="t('settingMenu.noStockCategories')"
            >
              <el-table-column prop="category_index" :label="t('settingMenu.sortIndex')" width="80" align="right" />
              <el-table-column prop="category_id" :label="t('settingMenu.categoryId')" min-width="120" />
              <el-table-column prop="name" :label="t('common.name')" min-width="200" />
              <el-table-column :label="t('common.enable')" width="80">
                <template #default="{ row }">
                  <StatusBadge :value="row.in_use" />
                </template>
              </el-table-column>
              <el-table-column :label="t('common.actions')" width="160" fixed="right">
                <template #default="{ row }">
                  <RowActions variant="link" @edit="openEditStockCategory(row)" @delete="handleDeleteStockCategory(row)" />
                </template>
              </el-table-column>
            </el-table>
          </div>
        </DataListCard>
      </el-tab-pane>
    </el-tabs>

    <FormDialog
      v-model="creditCardDialogVisible"
      :title="creditCardFormMode === 'create' ? t('settingMenu.createCreditCard') : t('settingMenu.editCreditCard')"
      :loading="creditCardSubmitting"
      width="540px"
      @submit="submitCreditCard"
    >
      <el-form
        ref="creditCardFormRef"
        :model="creditCardForm"
        :rules="creditCardFormRules"
        label-width="100px"
      >
        <el-form-item :label="t('settingMenu.cardId')" prop="credit_card_id">
          <el-input
            v-model="creditCardForm.credit_card_id"
            :disabled="creditCardFormMode === 'edit'"
            :placeholder="t('settingMenu.phCardId')"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.cardName')" prop="card_name">
          <el-input v-model="creditCardForm.card_name" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.cardNo')">
          <el-input v-model="cardNoModel" :placeholder="t('settingMenu.phCardNo')" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.lastDay')">
          <el-input-number
            v-model="lastDayModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.chargeDay')">
          <el-input-number
            v-model="chargeDayModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.limitDate')">
          <el-input-number
            v-model="limitDateModel"
            :min="1"
            :max="31"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.feedbackWay')">
          <el-input v-model="feedbackWayModel" :placeholder="t('settingMenu.phFeedbackWay')" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.fxCode')" prop="fx_code">
          <el-input v-model="creditCardForm.fx_code" />
        </el-form-item>
        <el-form-item :label="t('common.enable')">
          <el-radio-group v-model="creditCardForm.in_use">
            <el-radio value="Y">{{ t('settingMenu.enableLabel') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.disableLabel') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('settingMenu.sortIndex')">
          <el-input-number
            v-model="creditCardIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input v-model="creditCardNoteModel" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="stockCategoryDialogVisible"
      :title="stockCategoryFormMode === 'create' ? t('settingMenu.createStockCategory') : t('settingMenu.editStockCategory')"
      :loading="stockCategorySubmitting"
      width="460px"
      @submit="submitStockCategory"
    >
      <el-form
        ref="stockCategoryFormRef"
        :model="stockCategoryForm"
        :rules="stockCategoryFormRules"
        label-width="100px"
      >
        <el-form-item v-if="stockCategoryFormMode === 'edit'" :label="t('settingMenu.categoryId')">
          <el-input :model-value="String(editingStockCategoryId ?? '')" disabled />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="name">
          <el-input v-model="stockCategoryForm.name" :placeholder="t('settingMenu.phStockCategoryName')" />
        </el-form-item>
        <el-form-item :label="t('common.enable')">
          <el-radio-group v-model="stockCategoryForm.in_use">
            <el-radio value="Y">{{ t('settingMenu.enableLabel') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.disableLabel') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('settingMenu.sortIndex')">
          <el-input-number
            v-model="stockCategoryIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">
            {{ t('settingMenu.stockCategoryIndexHint') }}
          </p>
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="codeDialogVisible"
      :title="codeFormMode === 'create' ? t('settingMenu.createMainCode') : t('settingMenu.editMainCode')"
      :loading="codeSubmitting"
      width="520px"
      @submit="submitCode"
    >
      <el-form
        ref="codeFormRef"
        :model="codeForm"
        :rules="codeFormRules"
        label-width="100px"
      >
        <el-form-item :label="t('settingMenu.codeId')" prop="code_id">
          <el-input
            v-model="codeForm.code_id"
            :disabled="codeFormMode === 'edit'"
            :placeholder="t('settingMenu.phCodeId')"
          />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="code_type">
          <el-select v-model="codeForm.code_type" style="width: 100%">
            <el-option
              v-for="opt in CODE_TYPE_OPTIONS"
              :key="opt"
              :label="opt"
              :value="opt"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="name">
          <el-input v-model="codeForm.name" />
        </el-form-item>
        <el-form-item :label="t('common.enable')">
          <el-radio-group v-model="codeForm.in_use">
            <el-radio value="Y">{{ t('settingMenu.enableLabel') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.disableLabel') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('settingMenu.sortIndex')">
          <el-input-number
            v-model="codeIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.annualEvent')">
          <div class="flex flex-col gap-1">
            <el-switch v-model="codeForm.is_annual_event" />
            <span class="text-xs text-on-surface-muted">
              {{ t('settingMenu.annualEventHint') }}
            </span>
          </div>
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="subCodeDialogVisible"
      :title="subCodeFormMode === 'create' ? t('settingMenu.createSubCode') : t('settingMenu.editSubCode')"
      :loading="subCodeSubmitting"
      width="480px"
      @submit="submitSubCode"
    >
      <el-form
        ref="subCodeFormRef"
        :model="subCodeForm"
        :rules="subCodeFormRules"
        label-width="100px"
      >
        <el-form-item :label="t('settingMenu.parentCode')">
          <el-input :model-value="subCodeForm.parent_id ?? ''" disabled />
        </el-form-item>
        <el-form-item :label="t('settingMenu.subCodeId')" prop="code_id">
          <el-input
            v-model="subCodeForm.code_id"
            :disabled="subCodeFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="name">
          <el-input v-model="subCodeForm.name" />
        </el-form-item>
        <el-form-item :label="t('common.enable')">
          <el-radio-group v-model="subCodeForm.in_use">
            <el-radio value="Y">{{ t('settingMenu.enableLabel') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.disableLabel') }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </FormDialog>

    <FormDialog
      v-model="accountDialogVisible"
      :title="accountFormMode === 'create' ? t('settingMenu.createAccount') : t('settingMenu.editAccount')"
      :loading="accountSubmitting"
      width="540px"
      @submit="submitAccount"
    >
      <el-form
        ref="accountFormRef"
        :model="accountForm"
        :rules="accountFormRules"
        label-width="100px"
      >
        <el-form-item :label="t('settingMenu.accountId')" prop="account_id">
          <el-input
            v-model="accountForm.account_id"
            :disabled="accountFormMode === 'edit'"
            :placeholder="t('settingMenu.phAccountId')"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="name">
          <el-input v-model="accountForm.name" />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="account_type">
          <el-input v-model="accountForm.account_type" :placeholder="t('settingMenu.phAccountType')" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.fxCode')" prop="fx_code">
          <el-input v-model="accountForm.fx_code" :placeholder="t('settingMenu.phFxCode')" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.isCalculate')">
          <el-radio-group v-model="accountForm.is_calculate">
            <el-radio value="Y">{{ t('settingMenu.yes') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.no') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('common.enable')">
          <el-radio-group v-model="accountForm.in_use">
            <el-radio value="Y">{{ t('settingMenu.enableLabel') }}</el-radio>
            <el-radio value="N">{{ t('settingMenu.disableLabel') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('settingMenu.discount')">
          <el-input-number
            v-model="accountForm.discount"
            :precision="4"
            :step="0.01"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('settingMenu.owner')">
          <el-input v-model="ownerModel" />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input v-model="memoModel" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item :label="t('settingMenu.sortIndex')">
          <el-input-number
            v-model="accountIndexModel"
            :min="0"
            :step="1"
            :precision="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { type FormInstance, type FormRules } from 'element-plus'
import { Plus as PlusIcon } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import RowActions from '@/components/ui/RowActions.vue'
import { useCrudDialog } from '@/composables/useCrudDialog'
import { useSettingStore } from '@/stores/setting'
import {
  createAccount,
  updateAccount,
  deleteAccount,
  createCode,
  updateCode,
  deleteCode,
  createSubCode,
  updateSubCode,
  deleteSubCode,
  createCreditCard,
  updateCreditCard,
  deleteCreditCard,
  createStockCategory,
  updateStockCategory,
  deleteStockCategory,
} from '@/api/setting'
import type {
  Account,
  AccountCreate,
  CodeData,
  CodeDataCreate,
  CodeDataWithSub,
  CreditCard,
  CreditCardCreate,
  StockCategory,
  StockCategoryCreate,
} from '@/types/models'

const CODE_TYPE_OPTIONS = ['Floating', 'Fixed', 'Invest', 'Income', 'Transfer'] as const

const store = useSettingStore()
const { t } = useI18n()

const activeTab = ref<'accounts' | 'codes' | 'credit-cards' | 'stock-categories'>('accounts')

onMounted(() => {
  void store.fetchAccounts()
})

const codesLoaded = ref(false)
const creditCardsLoaded = ref(false)
const stockCategoriesLoaded = ref(false)
watch(activeTab, (tab) => {
  if (tab === 'codes' && !codesLoaded.value) {
    codesLoaded.value = true
    void store.fetchCodesWithSub()
  }
  if (tab === 'credit-cards' && !creditCardsLoaded.value) {
    creditCardsLoaded.value = true
    void store.fetchCreditCards()
  }
  if (tab === 'stock-categories' && !stockCategoriesLoaded.value) {
    stockCategoriesLoaded.value = true
    void store.fetchStockCategories()
  }
})

// ─── Account dialog ──────────────────────────────────────────────────────────

const accountFormRef = ref<FormInstance>()

function emptyAccountForm(): AccountCreate {
  return {
    account_id: '',
    name: '',
    account_type: '',
    fx_code: 'TWD',
    is_calculate: 'Y',
    in_use: 'Y',
    discount: 1,
    memo: null,
    owner: null,
    account_index: undefined,
  }
}

const accountFormRules = computed<FormRules>(() => ({
  account_id: [{ required: true, message: t('validation.enterAccountId'), trigger: 'blur' }],
  name: [{ required: true, message: t('settingMenu.enterName'), trigger: 'blur' }],
  account_type: [{ required: true, message: t('settingMenu.enterType'), trigger: 'blur' }],
  fx_code: [{ required: true, message: t('settingMenu.enterFxCode'), trigger: 'blur' }],
}))

const {
  dialogVisible: accountDialogVisible,
  formMode: accountFormMode,
  submitting: accountSubmitting,
  form: accountForm,
  openCreate: openCreateAccount,
  openEdit: openEditAccount,
  submit: submitAccount,
  remove: handleDeleteAccount,
} = useCrudDialog<Account, AccountCreate>({
  formRef: accountFormRef,
  emptyForm: emptyAccountForm,
  toForm: (row) => ({
    account_id: row.account_id,
    name: row.name,
    account_type: row.account_type,
    fx_code: row.fx_code,
    is_calculate: row.is_calculate,
    in_use: row.in_use,
    discount: row.discount,
    memo: row.memo ?? null,
    owner: row.owner ?? null,
    account_index: row.account_index,
  }),
  getId: (row) => row.id,
  create: (form) => createAccount({ ...form }),
  update: (id, form) => {
    const { account_id, ...rest } = form
    void account_id
    return updateAccount(id as number, rest)
  },
  remove: (id) => deleteAccount(id as number),
  refetch: () => store.fetchAccounts(),
  confirmDelete: (row) => ({
    title: t('settingMenu.deleteAccountTitle'),
    message: t('settingMenu.deleteAccountMsg', { name: row.name }),
  }),
})

const ownerModel = computed<string>({
  get: () => accountForm.value.owner ?? '',
  set: (v) => {
    accountForm.value.owner = v ? v : null
  },
})

const memoModel = computed<string>({
  get: () => accountForm.value.memo ?? '',
  set: (v) => {
    accountForm.value.memo = v ? v : null
  },
})

const accountIndexModel = computed<number | undefined>({
  get: () => accountForm.value.account_index,
  set: (v) => {
    accountForm.value.account_index = typeof v === 'number' ? v : undefined
  },
})

// ─── Main code dialog ────────────────────────────────────────────────────────

const codeFormRef = ref<FormInstance>()

function emptyCodeForm(): CodeDataCreate {
  return {
    code_id: '',
    code_type: 'Floating',
    name: '',
    parent_id: null,
    in_use: 'Y',
    code_index: undefined,
    is_annual_event: false,
  }
}

const codeFormRules = computed<FormRules>(() => ({
  code_id: [{ required: true, message: t('settingMenu.enterCodeId'), trigger: 'blur' }],
  code_type: [{ required: true, message: t('validation.pickType'), trigger: 'change' }],
  name: [{ required: true, message: t('settingMenu.enterName'), trigger: 'blur' }],
}))

const {
  dialogVisible: codeDialogVisible,
  formMode: codeFormMode,
  submitting: codeSubmitting,
  form: codeForm,
  openCreate: openCreateCode,
  openEdit: openEditCode,
  submit: submitCode,
  remove: handleDeleteCode,
} = useCrudDialog<CodeDataWithSub, CodeDataCreate>({
  formRef: codeFormRef,
  emptyForm: emptyCodeForm,
  toForm: (row) => ({
    code_id: row.code_id,
    code_type: row.code_type,
    name: row.name,
    parent_id: row.parent_id ?? null,
    in_use: row.in_use,
    code_index: row.code_index,
    is_annual_event: row.is_annual_event,
  }),
  getId: (row) => row.code_id,
  create: (form) => createCode({ ...form }),
  update: (id, form) => {
    const { code_id, ...rest } = form
    void code_id
    return updateCode(id as string, rest)
  },
  remove: (id) => deleteCode(id as string),
  refetch: () => store.fetchCodesWithSub(),
  confirmDelete: (row) => ({
    title: t('settingMenu.deleteMainCodeTitle'),
    message: t('settingMenu.deleteMainCodeMsg', { name: row.name }),
  }),
})

const codeIndexModel = computed<number | undefined>({
  get: () => codeForm.value.code_index,
  set: (v) => {
    codeForm.value.code_index = typeof v === 'number' ? v : undefined
  },
})

// ─── Sub-code dialog ─────────────────────────────────────────────────────────

const subCodeFormRef = ref<FormInstance>()
const subCodeParent = ref<CodeDataWithSub | null>(null)

function emptySubCodeForm(parent: CodeDataWithSub): CodeDataCreate {
  return {
    code_id: '',
    code_type: parent.code_type,
    name: '',
    parent_id: parent.code_id,
    in_use: 'Y',
    code_index: undefined,
  }
}

const subCodeFormRules = computed<FormRules>(() => ({
  code_id: [{ required: true, message: t('settingMenu.enterSubCodeId'), trigger: 'blur' }],
  name: [{ required: true, message: t('settingMenu.enterName'), trigger: 'blur' }],
}))

const {
  dialogVisible: subCodeDialogVisible,
  formMode: subCodeFormMode,
  submitting: subCodeSubmitting,
  form: subCodeForm,
  openCreate: openCreateSubCodeBase,
  openEdit: openEditSubCodeBase,
  submit: submitSubCode,
  remove: handleDeleteSubCode,
} = useCrudDialog<CodeData, CodeDataCreate>({
  formRef: subCodeFormRef,
  // The open* wrappers below always set `subCodeParent` before a dialog opens;
  // the null branch only covers the eager emptyForm() call during setup.
  emptyForm: () =>
    subCodeParent.value
      ? emptySubCodeForm(subCodeParent.value)
      : { code_id: '', code_type: '', name: '', parent_id: null, in_use: 'Y' },
  toForm: (row) => ({
    code_id: row.code_id,
    code_type: row.code_type || subCodeParent.value!.code_type,
    name: row.name,
    parent_id: subCodeParent.value!.code_id,
    in_use: row.in_use,
    code_index: row.code_index,
  }),
  getId: (row) => row.code_id,
  create: (form) => createSubCode({ ...form }),
  update: (id, form) => {
    const { code_id, ...rest } = form
    void code_id
    return updateSubCode(id as string, rest)
  },
  remove: (id) => deleteSubCode(id as string),
  refetch: () => store.fetchCodesWithSub(),
  confirmDelete: (row) => ({
    title: t('settingMenu.deleteSubCodeTitle'),
    message: t('settingMenu.deleteSubCodeMsg', { name: row.name }),
  }),
})

function openCreateSubCode(parent: CodeDataWithSub) {
  subCodeParent.value = parent
  openCreateSubCodeBase()
}

function openEditSubCode(parent: CodeDataWithSub, row: CodeData) {
  subCodeParent.value = parent
  openEditSubCodeBase(row)
}

// ─── Credit-card dialog ──────────────────────────────────────────────────────

const creditCardFormRef = ref<FormInstance>()

function emptyCreditCardForm(): CreditCardCreate {
  return {
    credit_card_id: '',
    card_name: '',
    card_no: null,
    last_day: null,
    charge_day: null,
    limit_date: null,
    feedback_way: null,
    fx_code: 'TWD',
    in_use: 'Y',
    credit_card_index: undefined,
    note: null,
  }
}

const creditCardFormRules = computed<FormRules>(() => ({
  credit_card_id: [{ required: true, message: t('settingMenu.enterCardId'), trigger: 'blur' }],
  card_name: [{ required: true, message: t('settingMenu.enterCardName'), trigger: 'blur' }],
  fx_code: [{ required: true, message: t('settingMenu.enterFxCode'), trigger: 'blur' }],
}))

const {
  dialogVisible: creditCardDialogVisible,
  formMode: creditCardFormMode,
  submitting: creditCardSubmitting,
  form: creditCardForm,
  openCreate: openCreateCreditCard,
  openEdit: openEditCreditCard,
  submit: submitCreditCard,
  remove: handleDeleteCreditCard,
} = useCrudDialog<CreditCard, CreditCardCreate>({
  formRef: creditCardFormRef,
  emptyForm: emptyCreditCardForm,
  toForm: (row) => ({
    credit_card_id: row.credit_card_id,
    card_name: row.card_name,
    card_no: row.card_no ?? null,
    last_day: row.last_day ?? null,
    charge_day: row.charge_day ?? null,
    limit_date: row.limit_date ?? null,
    feedback_way: row.feedback_way ?? null,
    fx_code: row.fx_code,
    in_use: row.in_use,
    credit_card_index: row.credit_card_index,
    note: row.note ?? null,
  }),
  getId: (row) => row.credit_card_id,
  create: (form) => createCreditCard({ ...form }),
  update: (id, form) => {
    const { credit_card_id, ...rest } = form
    void credit_card_id
    return updateCreditCard(id as string, rest)
  },
  remove: (id) => deleteCreditCard(id as string),
  refetch: () => store.fetchCreditCards(),
  confirmDelete: (row) => ({
    title: t('settingMenu.deleteCreditCardTitle'),
    message: t('settingMenu.deleteCreditCardMsg', { name: row.card_name }),
  }),
})

const cardNoModel = computed<string>({
  get: () => creditCardForm.value.card_no ?? '',
  set: (v) => {
    creditCardForm.value.card_no = v ? v : null
  },
})

function makeNumberNullableModel(field: 'last_day' | 'charge_day' | 'limit_date') {
  return computed<number | undefined>({
    get: () => creditCardForm.value[field] ?? undefined,
    set: (v) => {
      creditCardForm.value[field] = typeof v === 'number' ? v : null
    },
  })
}

const lastDayModel = makeNumberNullableModel('last_day')
const chargeDayModel = makeNumberNullableModel('charge_day')
const limitDateModel = makeNumberNullableModel('limit_date')

const feedbackWayModel = computed<string>({
  get: () => creditCardForm.value.feedback_way ?? '',
  set: (v) => {
    creditCardForm.value.feedback_way = v ? v : null
  },
})

const creditCardIndexModel = computed<number | undefined>({
  get: () => creditCardForm.value.credit_card_index,
  set: (v) => {
    creditCardForm.value.credit_card_index = typeof v === 'number' ? v : undefined
  },
})

const creditCardNoteModel = computed<string>({
  get: () => creditCardForm.value.note ?? '',
  set: (v) => {
    creditCardForm.value.note = v ? v : null
  },
})

// ─── Stock category dialog ───────────────────────────────────────────────────

const stockCategoryFormRef = ref<FormInstance>()

function emptyStockCategoryForm(): StockCategoryCreate {
  return { name: '', in_use: 'Y', category_index: undefined }
}

const stockCategoryFormRules = computed<FormRules>(() => ({
  name: [{ required: true, message: t('settingMenu.enterName'), trigger: 'blur' }],
}))

const {
  dialogVisible: stockCategoryDialogVisible,
  formMode: stockCategoryFormMode,
  submitting: stockCategorySubmitting,
  form: stockCategoryForm,
  editingId: editingStockCategoryId,
  openCreate: openCreateStockCategory,
  openEdit: openEditStockCategory,
  submit: submitStockCategory,
  remove: handleDeleteStockCategory,
} = useCrudDialog<StockCategory, StockCategoryCreate>({
  formRef: stockCategoryFormRef,
  emptyForm: emptyStockCategoryForm,
  toForm: (row) => ({
    name: row.name,
    in_use: row.in_use,
    category_index: row.category_index,
  }),
  getId: (row) => row.category_id,
  create: (form) => createStockCategory({ ...form }),
  update: (id, form) =>
    updateStockCategory(id as string, {
      name: form.name,
      in_use: form.in_use,
      category_index: form.category_index,
    }),
  remove: (id) => deleteStockCategory(id as string),
  refetch: () => store.fetchStockCategories(),
  confirmDelete: (row) => ({
    title: t('settingMenu.deleteStockCategoryTitle'),
    message: t('settingMenu.deleteStockCategoryMsg', { name: row.name }),
  }),
})

const stockCategoryIndexModel = computed<number | undefined>({
  get: () => stockCategoryForm.value.category_index,
  set: (v) => {
    stockCategoryForm.value.category_index = typeof v === 'number' ? v : undefined
  },
})
</script>

<style scoped>
.settings-tabs :deep(.el-tabs__nav-wrap::after) {
  background-color: var(--ds-color-outline-variant);
}
</style>
