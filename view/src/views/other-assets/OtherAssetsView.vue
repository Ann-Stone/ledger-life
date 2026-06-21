<template>
  <div class="flex flex-col gap-8">
    <PageHeader :title="t('otherAssets.pageTitle')" :subtitle="t('otherAssets.pageSubtitle')" />

    <el-tabs v-model="activeTab" class="other-assets-tabs">
      <!-- ─── Stocks ─────────────────────────────────────────── -->
      <el-tab-pane :label="t('otherAssets.tabStocks')" name="stocks">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('otherAssets.stocksSection')">
            <template #actions>
              <el-select
                v-model="stocksAssetId"
                :placeholder="t('otherAssets.pickCategory')"
                style="width: 240px"
                :disabled="stockCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in stockCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!stocksAssetId"
                @click="openCreateStock"
              >
                {{ t('common.add') }}
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.stocksLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!stocksAssetId"
            :message="t('otherAssets.pickCategoryFirst')"
          />
          <EmptyState
            v-else-if="store.stocks.length === 0"
            :message="t('otherAssets.noStocks')"
          />
          <el-table
            v-else
            :data="stockRows"
            row-key="stock_id"
            stripe
            border
            style="width: 100%"
            @expand-change="onStockExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <AssetDetailPanel
                  :title="t('otherAssets.stockDetailHeader')"
                  :rows="stockDetailsByStock.get(row.stock_id) ?? []"
                  :loading="stockDetailsLoadingByStock.get(row.stock_id) ?? false"
                  :empty-message="t('otherAssets.noStockDetails')"
                  type-field="excute_type"
                  :type-labels="stockTypeLabels"
                  account-field="account_name"
                >
                  <template #actions>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateStockDetail(row)"
                    >
                      {{ t('otherAssets.addDetail') }}
                    </el-button>
                  </template>
                  <template #summary="{ setAccount, accountFilter }">
                    <StockAccountSummary
                      :rows="stockDetailsByStock.get(row.stock_id) ?? []"
                      :currency="row.pnl?.fx_code ?? 'TWD'"
                      :active-account="accountFilter"
                      @select-account="setAccount"
                    />
                  </template>
                  <template #default="{ rows: dRows }">
                    <el-table :data="dRows" border size="small" max-height="360">
                      <el-table-column prop="excute_date" :label="t('common.date')" width="110" />
                      <el-table-column :label="t('common.type')" width="110">
                        <template #default="{ row: d }">
                          {{ stockTypeLabels[d.excute_type] ?? d.excute_type }}
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('otherAssets.colQuantity')" width="120" align="right">
                        <template #default="{ row: d }">
                          {{ d.excute_amount }}
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('otherAssets.colUnitPrice')" width="160" align="right">
                        <template #default="{ row: d }">
                          <MoneyDisplay :amount="d.excute_price" size="sm" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="account_name" :label="t('otherAssets.colSettleAccount')" min-width="160" />
                      <el-table-column prop="memo" :label="t('common.note')" min-width="120">
                        <template #default="{ row: d }">
                          <span>{{ d.memo ?? '' }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.actions')" width="180" align="center">
                        <template #default="{ row: d }">
                          <RowActions
                            @edit="openEditStockDetail(row, d)"
                            @delete="handleDeleteStockDetail(row, d)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </template>
                </AssetDetailPanel>
              </template>
            </el-table-column>
            <el-table-column prop="stock_id" :label="t('otherAssets.colStockId')" width="160" />
            <el-table-column prop="stock_code" :label="t('otherAssets.colCode')" width="140" />
            <el-table-column prop="stock_name" :label="t('common.name')" min-width="200" />
            <el-table-column :label="t('otherAssets.colAllocation')" width="120">
              <template #default="{ row }">
                <span>{{ row.category_id ? (allocationCategoryNameById.get(row.category_id) ?? row.category_id) : '—' }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colExpectedSpend')" width="140" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.expected_spend" size="sm" />
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colCost')" width="140" align="right">
              <template #default="{ row }">
                <MoneyDisplay
                  v-if="row.pnl"
                  :amount="row.pnl.cost"
                  :currency="row.pnl.fx_code"
                  size="sm"
                />
                <span v-else class="text-on-surface-variant/40">—</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colMarketValue')" width="140" align="right">
              <template #default="{ row }">
                <MoneyDisplay
                  v-if="row.pnl && row.pnl.market_value != null"
                  :amount="row.pnl.market_value"
                  :currency="row.pnl.fx_code"
                  size="sm"
                />
                <span v-else class="text-on-surface-variant/40">—</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colRealizedPnl')" width="170" align="right">
              <template #default="{ row }">
                <MoneyDisplay
                  v-if="row.pnl"
                  :amount="row.pnl.realized + row.pnl.dividends_total"
                  :currency="row.pnl.fx_code"
                  :positive="row.pnl.realized + row.pnl.dividends_total >= 0"
                  size="sm"
                />
                <span v-else class="text-on-surface-variant/40">—</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colUnrealizedPnl')" width="170" align="right">
              <template #default="{ row }">
                <div
                  v-if="row.pnl && row.pnl.unrealized != null"
                  class="flex flex-col items-end leading-tight"
                >
                  <MoneyDisplay
                    :amount="row.pnl.unrealized"
                    :currency="row.pnl.fx_code"
                    :positive="row.pnl.unrealized >= 0"
                    size="sm"
                  />
                  <span
                    class="text-xs tabular-nums"
                    :class="row.pnl.unrealized >= 0 ? 'text-positive' : 'text-negative'"
                  >{{ formatSignedPct(row.pnl.unrealized_pct) }}</span>
                </div>
                <span v-else class="text-on-surface-variant/40">—</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colCashYield')" width="120" align="right">
              <template #default="{ row }">
                <SharePercent :value="pct100(row.pnl?.cash_yield)" />
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colCostYield')" width="120" align="right">
              <template #default="{ row }">
                <SharePercent :value="pct100(row.pnl?.cost_yield)" />
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="160" align="center" fixed="right">
              <template #default="{ row }">
                <RowActions @edit="openEditStock(row)" @delete="handleDeleteStock(row)" />
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Estates ────────────────────────────────────────── -->
      <el-tab-pane :label="t('otherAssets.tabEstates')" name="estates">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('otherAssets.estatesSection')">
            <template #actions>
              <el-select
                v-model="estatesAssetId"
                :placeholder="t('otherAssets.pickCategory')"
                style="width: 240px"
                :disabled="estateCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in estateCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!estatesAssetId"
                @click="openCreateEstate"
              >
                {{ t('common.add') }}
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.estatesLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!estatesAssetId"
            :message="t('otherAssets.pickCategoryFirst')"
          />
          <EmptyState
            v-else-if="store.estates.length === 0"
            :message="t('otherAssets.noEstates')"
          />
          <el-table
            v-else
            :data="store.estates"
            stripe
            border
            style="width: 100%"
            @expand-change="onEstateExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <AssetDetailPanel
                  :title="t('otherAssets.estateDetailHeader')"
                  :rows="estateDetailsByEstate.get(row.estate_id) ?? []"
                  :loading="estateDetailsLoadingByEstate.get(row.estate_id) ?? false"
                  :empty-message="t('otherAssets.noEstateDetails')"
                  type-field="estate_excute_type"
                  :type-labels="estateTypeLabels"
                >
                  <template #actions>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateEstateDetail(row)"
                    >
                      {{ t('otherAssets.addDetail') }}
                    </el-button>
                  </template>
                  <template #default="{ rows: dRows }">
                    <el-table :data="dRows" border size="small" max-height="360">
                      <el-table-column prop="excute_date" :label="t('common.date')" width="110" />
                      <el-table-column :label="t('common.type')" width="120">
                        <template #default="{ row: d }">
                          {{ estateTypeLabels[d.estate_excute_type] ?? d.estate_excute_type }}
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.amount')" width="180" align="right">
                        <template #default="{ row: d }">
                          <MoneyDisplay :amount="d.excute_price" size="sm" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="memo" :label="t('common.note')" min-width="160">
                        <template #default="{ row: d }">
                          <span>{{ d.memo ?? '' }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.actions')" width="180" align="center">
                        <template #default="{ row: d }">
                          <RowActions
                            @edit="openEditEstateDetail(row, d)"
                            @delete="handleDeleteEstateDetail(row, d)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </template>
                </AssetDetailPanel>
              </template>
            </el-table-column>
            <el-table-column prop="estate_id" label="ID" width="140" />
            <el-table-column prop="estate_name" :label="t('common.name')" min-width="160" />
            <el-table-column prop="estate_type" :label="t('common.type')" width="120" />
            <el-table-column prop="estate_address" :label="t('otherAssets.colAddress')" min-width="200" />
            <el-table-column prop="obtain_date" :label="t('otherAssets.colObtainDate')" width="120" />
            <el-table-column :label="t('common.status')" width="100">
              <template #default="{ row }">
                <StatusBadge :variant="estateStatusVariant(row.estate_status)">
                  {{ row.estate_status }}
                </StatusBadge>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="180" align="center">
              <template #default="{ row }">
                <RowActions @edit="openEditEstate(row)" @delete="handleDeleteEstate(row)" />
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Insurances ─────────────────────────────────────── -->
      <el-tab-pane :label="t('otherAssets.tabInsurances')" name="insurances">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('otherAssets.insurancesSection')">
            <template #actions>
              <el-select
                v-model="insurancesAssetId"
                :placeholder="t('otherAssets.pickCategory')"
                style="width: 240px"
                :disabled="insuranceCategoryOptions.length === 0"
              >
                <el-option
                  v-for="cat in insuranceCategoryOptions"
                  :key="cat.asset_id"
                  :label="cat.asset_name"
                  :value="cat.asset_id"
                />
              </el-select>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                :disabled="!insurancesAssetId"
                @click="openCreateInsurance"
              >
                {{ t('common.add') }}
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.insurancesLoading" :rows="4" animated />
          <EmptyState
            v-else-if="!insurancesAssetId"
            :message="t('otherAssets.pickCategoryFirst')"
          />
          <EmptyState
            v-else-if="store.insurances.length === 0"
            :message="t('otherAssets.noInsurances')"
          />
          <el-table
            v-else
            :data="store.insurances"
            stripe
            border
            style="width: 100%"
            @expand-change="onInsuranceExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <AssetDetailPanel
                  :title="t('otherAssets.insuranceDetailHeader')"
                  :rows="insuranceDetailsByPolicy.get(row.insurance_id) ?? []"
                  :loading="insuranceDetailsLoadingByPolicy.get(row.insurance_id) ?? false"
                  :empty-message="t('otherAssets.noInsuranceDetails')"
                  type-field="insurance_excute_type"
                  :type-labels="insuranceTypeLabels"
                >
                  <template #actions>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateInsuranceDetail(row)"
                    >
                      {{ t('otherAssets.addDetail') }}
                    </el-button>
                  </template>
                  <template #default="{ rows: dRows }">
                    <el-table :data="dRows" border size="small" max-height="360">
                      <el-table-column prop="excute_date" :label="t('common.date')" width="110" />
                      <el-table-column :label="t('common.type')" width="120">
                        <template #default="{ row: d }">
                          {{ insuranceTypeLabels[d.insurance_excute_type] ?? d.insurance_excute_type }}
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.amount')" width="180" align="right">
                        <template #default="{ row: d }">
                          <MoneyDisplay :amount="d.excute_price" size="sm" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="memo" :label="t('common.note')" min-width="160">
                        <template #default="{ row: d }">
                          <span>{{ d.memo ?? '' }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.actions')" width="180" align="center">
                        <template #default="{ row: d }">
                          <RowActions
                            @edit="openEditInsuranceDetail(row, d)"
                            @delete="handleDeleteInsuranceDetail(row, d)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </template>
                </AssetDetailPanel>
              </template>
            </el-table-column>
            <el-table-column prop="insurance_id" label="ID" width="140" />
            <el-table-column prop="insurance_name" :label="t('common.name')" min-width="200" />
            <el-table-column prop="pay_type" :label="t('otherAssets.colPayType')" width="120" />
            <el-table-column prop="pay_day" :label="t('otherAssets.colPayDay')" width="90" align="right" />
            <el-table-column :label="t('otherAssets.colExpectedPremium')" width="180" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.expected_spend" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="start_date" :label="t('otherAssets.colStartDate')" width="110" />
            <el-table-column prop="end_date" :label="t('otherAssets.colEndDate')" width="110" />
            <el-table-column :label="t('otherAssets.colHasClosed')" width="90">
              <template #default="{ row }">
                <StatusBadge :value="row.has_closed" />
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="180" align="center">
              <template #default="{ row }">
                <RowActions @edit="openEditInsurance(row)" @delete="handleDeleteInsurance(row)" />
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Loans ──────────────────────────────────────────── -->
      <el-tab-pane :label="t('otherAssets.tabLoans')" name="loans">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('otherAssets.loansSection')">
            <template #actions>
              <el-button type="primary" :icon="Plus" size="small" @click="openCreateLoan">
                {{ t('common.add') }}
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.loansLoading" :rows="4" animated />
          <EmptyState v-else-if="store.loans.length === 0" :message="t('otherAssets.noLoans')" />
          <el-table
            v-else
            :data="store.loans"
            stripe
            border
            style="width: 100%"
            @expand-change="onLoanExpandChange"
          >
            <el-table-column type="expand">
              <template #default="{ row }">
                <AssetDetailPanel
                  :title="t('otherAssets.loanDetailHeader')"
                  :rows="loanDetailsByLoan.get(row.loan_id) ?? []"
                  :loading="loanDetailsLoadingByLoan.get(row.loan_id) ?? false"
                  :empty-message="t('otherAssets.noLoanDetails')"
                  type-field="loan_excute_type"
                  :type-labels="loanTypeLabels"
                >
                  <template #actions>
                    <el-button
                      type="primary"
                      :icon="Plus"
                      size="small"
                      @click="openCreateLoanDetail(row)"
                    >
                      {{ t('otherAssets.addDetail') }}
                    </el-button>
                  </template>
                  <template #default="{ rows: dRows }">
                    <el-table :data="dRows" border size="small" max-height="360">
                      <el-table-column prop="excute_date" :label="t('common.date')" width="110" />
                      <el-table-column :label="t('common.type')" width="120">
                        <template #default="{ row: d }">
                          {{ loanTypeLabels[d.loan_excute_type] ?? d.loan_excute_type }}
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.amount')" width="180" align="right">
                        <template #default="{ row: d }">
                          <MoneyDisplay :amount="d.excute_price" size="sm" />
                        </template>
                      </el-table-column>
                      <el-table-column prop="memo" :label="t('common.note')" min-width="160">
                        <template #default="{ row: d }">
                          <span>{{ d.memo ?? '' }}</span>
                        </template>
                      </el-table-column>
                      <el-table-column :label="t('common.actions')" width="180" align="center">
                        <template #default="{ row: d }">
                          <RowActions
                            @edit="openEditLoanDetail(row, d)"
                            @delete="handleDeleteLoanDetail(row, d)"
                          />
                        </template>
                      </el-table-column>
                    </el-table>
                  </template>
                </AssetDetailPanel>
              </template>
            </el-table-column>
            <el-table-column prop="loan_id" label="ID" width="120" />
            <el-table-column prop="loan_name" :label="t('common.name')" min-width="160" />
            <el-table-column prop="loan_type" :label="t('common.type')" width="120" />
            <el-table-column prop="account_name" :label="t('otherAssets.colRepayAccount')" min-width="140" />
            <el-table-column :label="t('otherAssets.colInterestRate')" width="100" align="right">
              <template #default="{ row }">
                {{ (row.interest_rate * 100).toFixed(2) }}%
              </template>
            </el-table-column>
            <el-table-column prop="period" :label="t('otherAssets.colPeriod')" width="80" align="right" />
            <el-table-column :label="t('otherAssets.colPrincipal')" width="160" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.amount" size="sm" />
              </template>
            </el-table-column>
            <el-table-column :label="t('otherAssets.colRepayed')" width="160" align="right">
              <template #default="{ row }">
                <MoneyDisplay :amount="row.repayed" size="sm" />
              </template>
            </el-table-column>
            <el-table-column prop="apply_date" :label="t('otherAssets.colApplyDate')" width="110" />
            <el-table-column :label="t('otherAssets.colGraceExpire')" width="120">
              <template #default="{ row }">
                <span>{{ row.grace_expire_date ?? '-' }}</span>
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="180" align="center">
              <template #default="{ row }">
                <RowActions @edit="openEditLoan(row)" @delete="handleDeleteLoan(row)" />
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>

      <!-- ─── Other-Assets ───────────────────────────────────── -->
      <el-tab-pane :label="t('otherAssets.tabOther')" name="other">
        <section class="flex flex-col gap-4">
          <SectionHeader :title="t('otherAssets.categoriesSection')">
            <template #actions>
              <el-button
                type="primary"
                :icon="Plus"
                size="small"
                @click="openCreateOtherAsset"
              >
                {{ t('common.add') }}
              </el-button>
            </template>
          </SectionHeader>

          <el-skeleton v-if="store.otherAssetsLoading" :rows="4" animated />
          <EmptyState
            v-else-if="otherAssetsSorted.length === 0"
            :message="t('otherAssets.noCategories')"
          />
          <el-table v-else :data="otherAssetsSorted" stripe border style="width: 100%">
            <el-table-column prop="asset_index" :label="t('otherAssets.colSortIndex')" width="80" align="right" />
            <el-table-column prop="asset_id" label="ID" width="160" />
            <el-table-column prop="asset_name" :label="t('common.name')" min-width="200" />
            <el-table-column prop="asset_type" :label="t('common.type')" width="140" />
            <el-table-column :label="t('otherAssets.enabled')" width="90">
              <template #default="{ row }">
                <StatusBadge :value="row.in_use" />
              </template>
            </el-table-column>
            <el-table-column :label="t('common.actions')" width="180" align="center">
              <template #default="{ row }">
                <RowActions @edit="openEditOtherAsset(row)" @delete="handleDeleteOtherAsset(row)" />
              </template>
            </el-table-column>
          </el-table>
        </section>
      </el-tab-pane>
    </el-tabs>

    <!-- ─── Stock Create / Edit Dialog ─────────────────────────────────────── -->
    <FormDialog
      v-model="stockDialogVisible"
      :title="stockFormMode === 'create' ? t('otherAssets.createStock') : t('otherAssets.editStock')"
      :loading="stockSubmitting"
      width="520px"
      @submit="submitStock"
    >
      <el-form
        ref="stockFormRef"
        :model="stockForm"
        :rules="stockFormRules"
        label-width="110px"
      >
        <el-form-item :label="t('otherAssets.colStockId')" prop="stock_id">
          <el-input
            v-model="stockForm.stock_id"
            :placeholder="t('otherAssets.stockIdPlaceholder')"
            :disabled="stockFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.colCode')" prop="stock_code">
          <el-input v-model="stockForm.stock_code" :placeholder="t('otherAssets.stockCodePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="stock_name">
          <el-input v-model="stockForm.stock_name" :placeholder="t('otherAssets.stockNamePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.assetCategory')">
          <el-input :model-value="stockForm.asset_id" disabled />
        </el-form-item>
        <el-form-item :label="t('otherAssets.colAllocation')">
          <el-select
            v-model="stockCategoryIdModel"
            :placeholder="t('otherAssets.allocationPlaceholder')"
            clearable
            style="width: 100%"
          >
            <el-option
              v-for="cat in allocationCategoryOptions"
              :key="cat.category_id"
              :label="cat.name"
              :value="cat.category_id"
            />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('otherAssets.colExpectedSpend')" prop="expected_spend">
          <el-input-number
            v-model="stockForm.expected_spend"
            :precision="2"
            :step="1000"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Stock Detail Create / Edit Dialog ──────────────────────────────── -->
    <FormDialog
      v-model="stockDetailDialogVisible"
      :title="stockDetailFormMode === 'create' ? t('otherAssets.createStockDetail') : t('otherAssets.editStockDetail')"
      :loading="stockDetailSubmitting"
      width="560px"
      @submit="submitStockDetail"
    >
      <el-form
        ref="stockDetailFormRef"
        :model="stockDetailForm"
        :rules="stockDetailFormRules"
        label-width="110px"
      >
        <StockDetailFormFields
          v-model="stockDetailForm"
          mode="asset-manage"
          show-stock-id-input
        />
      </el-form>
    </FormDialog>

    <!-- ─── Estate Create / Edit Dialog ────────────────────────────────────── -->
    <FormDialog
      v-model="estateDialogVisible"
      :title="estateFormMode === 'create' ? t('otherAssets.createEstate') : t('otherAssets.editEstate')"
      :loading="estateSubmitting"
      width="560px"
      @submit="submitEstate"
    >
      <el-form
        ref="estateFormRef"
        :model="estateForm"
        :rules="estateFormRules"
        label-width="110px"
      >
        <el-form-item :label="t('otherAssets.estateIdLabel')" prop="estate_id">
          <el-input
            v-model="estateForm.estate_id"
            :placeholder="t('otherAssets.estateIdPlaceholder')"
            :disabled="estateFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="estate_name">
          <el-input v-model="estateForm.estate_name" />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="estate_type">
          <el-input v-model="estateForm.estate_type" :placeholder="t('otherAssets.estateTypePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.colAddress')" prop="estate_address">
          <el-input v-model="estateForm.estate_address" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.assetCategory')">
          <el-input :model-value="estateForm.asset_id" disabled />
        </el-form-item>
        <el-form-item :label="t('otherAssets.fxCode')" prop="fx_code">
          <el-select v-model="estateForm.fx_code" style="width: 100%">
            <el-option :label="t('otherAssets.fxTwd')" value="TWD" />
            <el-option :label="t('otherAssets.fxUsd')" value="USD" />
            <el-option :label="t('otherAssets.fxJpy')" value="JPY" />
            <el-option :label="t('otherAssets.fxEur')" value="EUR" />
            <el-option :label="t('otherAssets.fxCny')" value="CNY" />
            <el-option :label="t('otherAssets.fxHkd')" value="HKD" />
            <el-option :label="t('otherAssets.fxGbp')" value="GBP" />
            <el-option :label="t('otherAssets.fxAud')" value="AUD" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('otherAssets.colObtainDate')" prop="obtain_date">
          <el-date-picker
            v-model="estateFormObtainDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('common.status')" prop="estate_status">
          <el-select v-model="estateForm.estate_status" style="width: 100%">
            <el-option :label="t('otherAssets.estateStatusIdle')" value="idle" />
            <el-option :label="t('otherAssets.estateStatusLive')" value="live" />
            <el-option :label="t('otherAssets.estateStatusRent')" value="rent" />
            <el-option :label="t('otherAssets.estateStatusSold')" value="sold" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('otherAssets.region')">
          <el-select
            v-model="estateForm.region"
            clearable
            :placeholder="t('otherAssets.regionPlaceholder')"
            style="width: 100%"
          >
            <el-option v-for="r in ESTATE_REGIONS" :key="r" :label="r" :value="r" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('otherAssets.linkedLoan')">
          <el-input v-model="estateLoanIdProxy" :placeholder="t('otherAssets.linkedLoanPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input v-model="estateMemoProxy" type="textarea" :rows="2" :placeholder="t('common.optional')" />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Insurance Create / Edit Dialog ─────────────────────────────────── -->
    <FormDialog
      v-model="insuranceDialogVisible"
      :title="insuranceFormMode === 'create' ? t('otherAssets.createInsurance') : t('otherAssets.editInsurance')"
      :loading="insuranceSubmitting"
      width="560px"
      @submit="submitInsurance"
    >
      <el-form
        ref="insuranceFormRef"
        :model="insuranceForm"
        :rules="insuranceFormRules"
        label-width="110px"
      >
        <el-form-item :label="t('otherAssets.insuranceIdLabel')" prop="insurance_id">
          <el-input
            v-model="insuranceForm.insurance_id"
            :placeholder="t('otherAssets.insuranceIdPlaceholder')"
            :disabled="insuranceFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="insurance_name">
          <el-input v-model="insuranceForm.insurance_name" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.assetCategory')">
          <el-input :model-value="insuranceForm.asset_id" disabled />
        </el-form-item>
        <el-form-item :label="t('otherAssets.inAccount')" prop="in_account">
          <el-input v-model="insuranceForm.in_account" :placeholder="t('otherAssets.inAccountPlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.outAccount')" prop="out_account">
          <el-input v-model="insuranceForm.out_account" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.startDate')" prop="start_date">
          <el-date-picker
            v-model="insuranceFormStartDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.endDate')" prop="end_date">
          <el-date-picker
            v-model="insuranceFormEndDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.payType')" prop="pay_type">
          <el-input v-model="insuranceForm.pay_type" :placeholder="t('otherAssets.payTypePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.payDay')" prop="pay_day">
          <el-input
            v-model="insuranceForm.pay_day"
            :placeholder="t('otherAssets.payDayPlaceholder')"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.expectedPremium')" prop="expected_spend">
          <el-input-number
            v-model="insuranceForm.expected_spend"
            :precision="2"
            :step="100"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.isClosed')" prop="has_closed">
          <el-radio-group v-model="insuranceForm.has_closed">
            <el-radio value="N">{{ t('otherAssets.notClosed') }}</el-radio>
            <el-radio value="Y">{{ t('otherAssets.closed') }}</el-radio>
          </el-radio-group>
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Insurance Detail Create / Edit Dialog ──────────────────────────── -->
    <FormDialog
      v-model="insuranceDetailDialogVisible"
      :title="insuranceDetailFormMode === 'create' ? t('otherAssets.createInsuranceDetail') : t('otherAssets.editInsuranceDetail')"
      :loading="insuranceDetailSubmitting"
      width="520px"
      @submit="submitInsuranceDetail"
    >
      <el-form
        ref="insuranceDetailFormRef"
        :model="insuranceDetailForm"
        :rules="insuranceDetailFormRules"
        label-width="110px"
      >
        <InsuranceDetailFormFields
          v-model="insuranceDetailForm"
          mode="asset-manage"
          show-insurance-id-input
        />
      </el-form>
    </FormDialog>

    <!-- ─── Other-Asset Create / Edit Dialog ───────────────────────────────── -->
    <FormDialog
      v-model="otherAssetDialogVisible"
      :title="otherAssetFormMode === 'create' ? t('otherAssets.createCategory') : t('otherAssets.editCategory')"
      :loading="otherAssetSubmitting"
      width="520px"
      @submit="submitOtherAsset"
    >
      <el-form
        ref="otherAssetFormRef"
        :model="otherAssetForm"
        :rules="otherAssetFormRules"
        label-width="110px"
      >
        <el-form-item label="ID" prop="asset_id">
          <el-input
            v-model="otherAssetForm.asset_id"
            :placeholder="t('otherAssets.categoryIdPlaceholder')"
            :disabled="otherAssetFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="asset_name">
          <el-input v-model="otherAssetForm.asset_name" />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="asset_type">
          <el-select v-model="otherAssetForm.asset_type" style="width: 100%" allow-create filterable>
            <el-option :label="t('otherAssets.assetTypeStock')" value="stock" />
            <el-option :label="t('otherAssets.assetTypeEstate')" value="estate" />
            <el-option :label="t('otherAssets.assetTypeInsurance')" value="insurance" />
            <el-option :label="t('otherAssets.assetTypeLoan')" value="loan" />
            <el-option :label="t('otherAssets.assetTypeOther')" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('otherAssets.enabled')" prop="in_use">
          <el-radio-group v-model="otherAssetForm.in_use">
            <el-radio value="Y">{{ t('otherAssets.enabled') }}</el-radio>
            <el-radio value="N">{{ t('otherAssets.disabled') }}</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item :label="t('otherAssets.sortIndex')">
          <el-input-number
            v-model="otherAssetIndexProxy"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">
            {{ t('otherAssets.sortAutoHint') }}
          </p>
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Loan Create / Edit Dialog ──────────────────────────────────────── -->
    <FormDialog
      v-model="loanDialogVisible"
      :title="loanFormMode === 'create' ? t('otherAssets.createLoan') : t('otherAssets.editLoan')"
      :loading="loanSubmitting"
      width="600px"
      @submit="submitLoan"
    >
      <el-form
        ref="loanFormRef"
        :model="loanForm"
        :rules="loanFormRules"
        label-width="120px"
      >
        <el-form-item :label="t('otherAssets.loanIdLabel')" prop="loan_id">
          <el-input
            v-model="loanForm.loan_id"
            :placeholder="t('otherAssets.loanIdPlaceholder')"
            :disabled="loanFormMode === 'edit'"
          />
        </el-form-item>
        <el-form-item :label="t('common.name')" prop="loan_name">
          <el-input v-model="loanForm.loan_name" />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="loan_type">
          <el-input v-model="loanForm.loan_type" :placeholder="t('otherAssets.loanTypePlaceholder')" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.repayAccountId')" prop="account_id">
          <el-input v-model="loanForm.account_id" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.repayAccountName')" prop="account_name">
          <el-input v-model="loanForm.account_name" />
        </el-form-item>
        <el-form-item :label="t('otherAssets.annualRate')" prop="interest_rate">
          <el-input-number
            v-model="loanForm.interest_rate"
            :precision="4"
            :step="0.001"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
          <p class="text-xs text-on-surface-variant mt-1">{{ t('otherAssets.annualRateHint') }}</p>
        </el-form-item>
        <el-form-item :label="t('otherAssets.periodMonths')" prop="period">
          <el-input-number
            v-model="loanForm.period"
            :min="1"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.colApplyDate')" prop="apply_date">
          <el-date-picker
            v-model="loanFormApplyDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.graceExpire')">
          <el-date-picker
            v-model="loanFormGraceDate"
            type="date"
            format="YYYY/MM/DD"
            :placeholder="t('common.optional')"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.payDay')" prop="pay_day">
          <el-input-number
            v-model="loanForm.pay_day"
            :min="1"
            :max="31"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.colPrincipal')" prop="amount">
          <el-input-number
            v-model="loanForm.amount"
            :precision="2"
            :step="10000"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('otherAssets.repayedPrincipal')" prop="repayed">
          <el-input-number
            v-model="loanForm.repayed"
            :precision="2"
            :step="1000"
            :min="0"
            :disabled="loanFormMode === 'edit'"
            controls-position="right"
            style="width: 100%"
          />
          <span v-if="loanFormMode === 'edit'" class="text-xs text-on-surface-muted ml-2">
            {{ t('otherAssets.repayedAuto') }}
          </span>
        </el-form-item>
        <el-form-item :label="t('otherAssets.sortIndex')" prop="loan_index">
          <el-input-number
            v-model="loanForm.loan_index"
            :min="0"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Loan Detail Create / Edit Dialog ───────────────────────────────── -->
    <FormDialog
      v-model="loanDetailDialogVisible"
      :title="loanDetailFormMode === 'create' ? t('otherAssets.createLoanDetail') : t('otherAssets.editLoanDetail')"
      :loading="loanDetailSubmitting"
      width="520px"
      @submit="submitLoanDetail"
    >
      <el-form
        ref="loanDetailFormRef"
        :model="loanDetailForm"
        :rules="loanDetailFormRules"
        label-width="110px"
      >
        <el-form-item :label="t('otherAssets.loanIdLabel')">
          <el-input :model-value="loanDetailForm.loan_id" disabled />
        </el-form-item>
        <el-form-item :label="t('common.date')" prop="excute_date">
          <el-date-picker
            v-model="loanDetailFormDate"
            type="date"
            format="YYYY/MM/DD"
            :clearable="false"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('common.type')" prop="loan_excute_type">
          <el-select v-model="loanDetailForm.loan_excute_type" style="width: 100%">
            <el-option :label="t('otherAssets.loanExTypePrincipal')" value="principal" />
            <el-option :label="t('otherAssets.loanExTypeInterest')" value="interest" />
            <el-option :label="t('otherAssets.loanExTypeIncrement')" value="increment" />
            <el-option :label="t('otherAssets.loanExTypeFee')" value="fee" />
          </el-select>
        </el-form-item>
        <el-form-item :label="t('common.amount')" prop="excute_price">
          <el-input-number
            v-model="loanDetailForm.excute_price"
            :precision="2"
            :step="100"
            controls-position="right"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item :label="t('common.note')">
          <el-input
            v-model="loanDetailMemoProxy"
            type="textarea"
            :rows="2"
            :placeholder="t('common.optional')"
          />
        </el-form-item>
      </el-form>
    </FormDialog>

    <!-- ─── Estate Detail Create / Edit Dialog ─────────────────────────────── -->
    <FormDialog
      v-model="estateDetailDialogVisible"
      :title="estateDetailFormMode === 'create' ? t('otherAssets.createEstateDetail') : t('otherAssets.editEstateDetail')"
      :loading="estateDetailSubmitting"
      width="520px"
      @submit="submitEstateDetail"
    >
      <el-form
        ref="estateDetailFormRef"
        :model="estateDetailForm"
        :rules="estateDetailFormRules"
        label-width="110px"
      >
        <EstateDetailFormFields
          v-model="estateDetailForm"
          mode="asset-manage"
          show-estate-id-input
        />
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, shallowReactive, watch } from 'vue'
import dayjs from 'dayjs'
import type { FormInstance, FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import PageHeader from '@/components/ui/PageHeader.vue'
import SectionHeader from '@/components/ui/SectionHeader.vue'
import EmptyState from '@/components/ui/EmptyState.vue'
import MoneyDisplay from '@/components/ui/MoneyDisplay.vue'
import SharePercent from '@/components/ui/SharePercent.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import StatusBadge from '@/components/ui/StatusBadge.vue'
import RowActions from '@/components/ui/RowActions.vue'
import StockDetailFormFields, {
  stockDetailFullRules,
} from '@/components/forms/StockDetailFormFields.vue'
import InsuranceDetailFormFields, {
  insuranceDetailFullRules,
} from '@/components/forms/InsuranceDetailFormFields.vue'
import EstateDetailFormFields, {
  estateDetailFullRules,
} from '@/components/forms/EstateDetailFormFields.vue'
import AssetDetailPanel from '@/views/other-assets/AssetDetailPanel.vue'
import StockAccountSummary from '@/views/other-assets/StockAccountSummary.vue'
import { useCrudDialog } from '@/composables/useCrudDialog'
import { useDateStringModel } from '@/composables/useDateStringModel'
import { todayYyyymmdd } from '@/utils/dateFormat'
import { useOtherAssetsStore } from '@/stores/otherAssets'
import { useSettingStore } from '@/stores/setting'
import {
  createEstate,
  createEstateDetail,
  createInsurance,
  createInsuranceDetail,
  createLoan,
  createLoanDetail,
  createOtherAsset,
  createStock,
  createStockDetail,
  deleteEstate,
  deleteEstateDetail,
  deleteInsurance,
  deleteInsuranceDetail,
  deleteLoan,
  deleteLoanDetail,
  deleteOtherAsset,
  deleteStock,
  deleteStockDetail,
  getEstateDetails,
  getInsuranceDetails,
  getLoanDetails,
  getStockDetails,
  updateEstate,
  updateEstateDetail,
  updateInsurance,
  updateInsuranceDetail,
  updateLoan,
  updateLoanDetail,
  updateOtherAsset,
  updateStock,
  updateStockDetail,
} from '@/api/otherAssets'
import type {
  EstateAsset,
  EstateAssetCreate,
  EstateJournal,
  EstateJournalCreate,
  InsuranceAsset,
  InsuranceAssetCreate,
  InsuranceJournal,
  InsuranceJournalCreate,
  LoanAsset,
  LoanAssetCreate,
  LoanJournal,
  LoanJournalCreate,
  OtherAsset,
  OtherAssetCreate,
  StockAsset,
  StockAssetCreate,
  StockJournal,
  StockJournalCreate,
  StockPnlSummary,
} from '@/types/models'

const store = useOtherAssetsStore()
const settingStore = useSettingStore()
const { t } = useI18n()

const activeTab = ref<string>('stocks')

// ─── Detail type labels (raw enum → readable) ───────────────────────────────
// Drives each panel's type-filter dropdown and the detail-table type column.
const stockTypeLabels = computed<Record<string, string>>(() => ({
  buy: t('otherAssets.exTypeBuy'),
  sell: t('otherAssets.exTypeSell'),
  stock: t('otherAssets.exTypeStockDiv'),
  cash: t('otherAssets.exTypeCashDiv'),
}))
const estateTypeLabels = computed<Record<string, string>>(() => ({
  tax: t('otherAssets.estateExTypeTax'),
  fee: t('otherAssets.estateExTypeFee'),
  insurance: t('otherAssets.estateExTypeInsurance'),
  fix: t('otherAssets.estateExTypeFix'),
  rent: t('otherAssets.estateExTypeRent'),
  deposit: t('otherAssets.estateExTypeDeposit'),
}))
const insuranceTypeLabels = computed<Record<string, string>>(() => ({
  pay: t('otherAssets.insExTypePay'),
  cash: t('otherAssets.insExTypeCash'),
  return: t('otherAssets.insExTypeReturn'),
  expect: t('otherAssets.insExTypeExpect'),
}))
const loanTypeLabels = computed<Record<string, string>>(() => ({
  principal: t('otherAssets.loanExTypePrincipal'),
  interest: t('otherAssets.loanExTypeInterest'),
  increment: t('otherAssets.loanExTypeIncrement'),
  fee: t('otherAssets.loanExTypeFee'),
}))

// ─── Stock category options ─────────────────────────────────────────────────
// Legacy data has mixed casing on asset_type ("Stock" vs "stock"); compare
// case-insensitively so both forms surface in the dropdown.
const stockCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type.toLowerCase() === 'stock' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const stocksAssetId = ref<string>('')

watch(stockCategoryOptions, (options) => {
  if (!stocksAssetId.value && options.length > 0) {
    stocksAssetId.value = options[0]!.asset_id
  }
})

watch(stocksAssetId, (assetId) => {
  if (assetId) void fetchStocks(assetId)
})

async function fetchStocks(assetId: string) {
  await Promise.all([store.fetchStocks(assetId), store.fetchStockPnl(assetId)])
}

// Computed P&L keyed by holding, merged onto each stock row so the table cells
// can read `row.pnl?.*` directly. row-key keeps expand state stable when the
// summary resolves and the merged rows are rebuilt.
const summaryByStock = computed(() => {
  const map = new Map<string, StockPnlSummary>()
  for (const s of store.stockPnl) map.set(s.stock_id, s)
  return map
})
const stockRows = computed(() =>
  store.stocks.map((s) => ({ ...s, pnl: summaryByStock.value.get(s.stock_id) ?? null })),
)

// Fraction (0.05) → percent number (5) for <SharePercent>; null passes through.
function pct100(frac: number | null | undefined): number | null {
  return frac == null ? null : frac * 100
}
// Signed percent string with explicit sign for the unrealized cell.
function formatSignedPct(frac: number | null | undefined): string {
  if (frac == null) return '—'
  const pct = frac * 100
  return `${pct >= 0 ? '+' : ''}${pct.toFixed(1)}%`
}

// ─── Stock allocation category (Stock_Category dictionary) ───────────────────
// Active categories feed the holding form's dropdown; the full list (including
// retired ones) backs the list-column name lookup so an existing holding keeps
// a readable label even after its category is disabled.
const allocationCategoryOptions = computed(() =>
  [...settingStore.stockCategories]
    .filter((c) => c.in_use === 'Y')
    .sort((a, b) => a.category_index - b.category_index),
)
const allocationCategoryNameById = computed(() => {
  const map = new Map<string, string>()
  for (const c of settingStore.stockCategories) map.set(c.category_id, c.name)
  return map
})

// ─── Stock create/edit form ─────────────────────────────────────────────────
const stockFormRef = ref<FormInstance>()

interface StockFormState extends StockAssetCreate {}

function emptyStockForm(): StockFormState {
  return {
    stock_id: '',
    stock_code: '',
    stock_name: '',
    asset_id: stocksAssetId.value,
    expected_spend: 0,
    category_id: null,
  }
}

const stockFormRules = computed<FormRules>(() => ({
  stock_id: [{ required: true, message: t('otherAssets.enterStockId'), trigger: 'blur' }],
  stock_code: [{ required: true, message: t('validation.enterCode'), trigger: 'blur' }],
  stock_name: [{ required: true, message: t('otherAssets.enterName'), trigger: 'blur' }],
  expected_spend: [{ required: true, message: t('otherAssets.enterExpectedSpend'), trigger: 'blur' }],
}))

const {
  dialogVisible: stockDialogVisible,
  formMode: stockFormMode,
  submitting: stockSubmitting,
  form: stockForm,
  openCreate: openCreateStock,
  openEdit: openEditStock,
  submit: submitStock,
  remove: handleDeleteStock,
} = useCrudDialog<StockAsset, StockFormState>({
  formRef: stockFormRef,
  emptyForm: emptyStockForm,
  toForm: (row) => ({
    stock_id: row.stock_id,
    stock_code: row.stock_code,
    stock_name: row.stock_name,
    asset_id: row.asset_id,
    expected_spend: row.expected_spend,
    category_id: row.category_id ?? null,
  }),
  getId: (row) => row.stock_id,
  create: (form) => createStock({ ...form }),
  update: (id, form) =>
    updateStock(id as string, {
      stock_code: form.stock_code,
      stock_name: form.stock_name,
      asset_id: form.asset_id,
      expected_spend: form.expected_spend,
      category_id: form.category_id ?? null,
    }),
  remove: (id) => deleteStock(id as string),
  refetch: () => {
    if (stocksAssetId.value) return fetchStocks(stocksAssetId.value)
  },
  confirmDelete: (row) => ({
    title: t('otherAssets.deleteStockTitle'),
    message: t('otherAssets.deleteStockMsg', { name: row.stock_name, code: row.stock_code }),
  }),
  onAfterDelete: (row) => {
    stockDetailsByStock.delete(row.stock_id)
  },
})

const stockCategoryIdModel = computed<string | undefined>({
  get: () => stockForm.value.category_id ?? undefined,
  set: (v) => {
    stockForm.value.category_id = v ? v : null
  },
})

// ─── Stock journal (details) ────────────────────────────────────────────────
const stockDetailsByStock = shallowReactive(new Map<string, StockJournal[]>())
const stockDetailsLoadingByStock = shallowReactive(new Map<string, boolean>())

async function fetchStockDetails(stockId: string) {
  stockDetailsLoadingByStock.set(stockId, true)
  try {
    const details = await getStockDetails(stockId)
    stockDetailsByStock.set(stockId, details)
  } finally {
    stockDetailsLoadingByStock.set(stockId, false)
  }
}

function onStockExpandChange(row: StockAsset, expanded: StockAsset[]) {
  const isExpanded = expanded.some((r) => r.stock_id === row.stock_id)
  if (isExpanded && !stockDetailsByStock.has(row.stock_id)) {
    void fetchStockDetails(row.stock_id)
  }
}

interface StockDetailFormState extends StockJournalCreate {
  distinct_number?: number
}

const stockDetailFormRef = ref<FormInstance>()
const stockDetailParent = ref<StockAsset | null>(null)

function emptyStockDetailForm(stockId: string): StockDetailFormState {
  return {
    stock_id: stockId,
    excute_type: 'buy',
    excute_amount: 0,
    excute_price: 0,
    excute_date: todayYyyymmdd(),
    account_id: '',
    account_name: '',
    memo: null,
  }
}

const stockDetailFormRules = computed(() => stockDetailFullRules(t))

function stockDetailPayload(form: StockDetailFormState): StockJournalCreate {
  return {
    stock_id: form.stock_id,
    excute_type: form.excute_type,
    excute_amount: Number(form.excute_amount ?? 0),
    excute_price: Number(form.excute_price ?? 0),
    excute_date: form.excute_date,
    account_id: form.account_id,
    account_name: form.account_name,
    memo: form.memo || null,
  }
}

const {
  dialogVisible: stockDetailDialogVisible,
  formMode: stockDetailFormMode,
  submitting: stockDetailSubmitting,
  form: stockDetailForm,
  openCreate: openCreateStockDetailBase,
  openEdit: openEditStockDetailBase,
  submit: submitStockDetail,
  remove: removeStockDetailBase,
} = useCrudDialog<StockJournal, StockDetailFormState>({
  formRef: stockDetailFormRef,
  emptyForm: () => emptyStockDetailForm(stockDetailParent.value?.stock_id ?? ''),
  toForm: (detail) => ({
    distinct_number: detail.distinct_number,
    stock_id: stockDetailParent.value!.stock_id,
    excute_type: detail.excute_type,
    excute_amount: detail.excute_amount,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    account_id: detail.account_id,
    account_name: detail.account_name,
    memo: detail.memo ?? null,
  }),
  getId: (detail) => detail.distinct_number,
  create: (form) => createStockDetail(form.stock_id, stockDetailPayload(form)),
  update: (id, form) => updateStockDetail(id as number, stockDetailPayload(form)),
  remove: (id) => deleteStockDetail(id as number),
  refetch: async () => {
    await fetchStockDetails(stockDetailParent.value!.stock_id)
    // Transactions changed → recompute this category's P&L summary.
    if (stocksAssetId.value) await store.fetchStockPnl(stocksAssetId.value)
  },
  confirmDelete: (detail) => ({
    title: t('otherAssets.deleteStockDetailTitle'),
    message: t('otherAssets.deleteStockDetailMsg', {
      date: detail.excute_date,
      type: detail.excute_type,
    }),
  }),
})

function openCreateStockDetail(stock: StockAsset) {
  stockDetailParent.value = stock
  openCreateStockDetailBase()
}

function openEditStockDetail(stock: StockAsset, detail: StockJournal) {
  stockDetailParent.value = stock
  openEditStockDetailBase(detail)
}

function handleDeleteStockDetail(stock: StockAsset, detail: StockJournal) {
  stockDetailParent.value = stock
  return removeStockDetailBase(detail)
}

// ─── Estates ────────────────────────────────────────────────────────────────
const estateCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type.toLowerCase() === 'estate' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const estatesAssetId = ref<string>('')

watch(estateCategoryOptions, (options) => {
  if (!estatesAssetId.value && options.length > 0) {
    estatesAssetId.value = options[0]!.asset_id
  }
})

watch(estatesAssetId, (assetId) => {
  if (assetId) void store.fetchEstates(assetId)
})

function estateStatusVariant(status: string): 'success' | 'info' | 'warning' | 'danger' {
  switch (status) {
    case 'live':
      return 'success'
    case 'rent':
      return 'warning'
    case 'sold':
      return 'danger'
    default:
      return 'info'
  }
}

const estateFormRef = ref<FormInstance>()

// House-price-index regions (內政部 住宅價格指數 covers 全國 + 6 直轄市). Clearing
// the select = 全國. Used to pick the index series for the suggested market value.
const ESTATE_REGIONS = ['全國', '臺北市', '新北市', '桃園市', '臺中市', '臺南市', '高雄市']

function emptyEstateForm(): EstateAssetCreate {
  return {
    estate_id: '',
    estate_name: '',
    estate_type: '',
    estate_address: '',
    asset_id: estatesAssetId.value,
    fx_code: 'TWD',
    obtain_date: todayYyyymmdd(),
    loan_id: null,
    estate_status: 'live',
    region: null,
    memo: null,
  }
}

const estateFormRules = computed<FormRules>(() => ({
  estate_id: [{ required: true, message: t('otherAssets.enterEstateId'), trigger: 'blur' }],
  estate_name: [{ required: true, message: t('otherAssets.enterName'), trigger: 'blur' }],
  estate_type: [{ required: true, message: t('otherAssets.enterType'), trigger: 'blur' }],
  estate_address: [{ required: true, message: t('otherAssets.enterAddress'), trigger: 'blur' }],
  obtain_date: [{ required: true, message: t('otherAssets.pickObtainDate'), trigger: 'change' }],
  estate_status: [{ required: true, message: t('otherAssets.pickStatus'), trigger: 'change' }],
}))

const {
  dialogVisible: estateDialogVisible,
  formMode: estateFormMode,
  submitting: estateSubmitting,
  form: estateForm,
  openCreate: openCreateEstate,
  openEdit: openEditEstate,
  submit: submitEstate,
  remove: handleDeleteEstate,
} = useCrudDialog<EstateAsset, EstateAssetCreate>({
  formRef: estateFormRef,
  emptyForm: emptyEstateForm,
  toForm: (row) => ({
    estate_id: row.estate_id,
    estate_name: row.estate_name,
    estate_type: row.estate_type,
    estate_address: row.estate_address,
    asset_id: row.asset_id,
    fx_code: row.fx_code ?? 'TWD',
    obtain_date: row.obtain_date,
    loan_id: row.loan_id ?? null,
    estate_status: row.estate_status,
    region: row.region ?? null,
    memo: row.memo ?? null,
  }),
  getId: (row) => row.estate_id,
  create: (form) => createEstate({ ...form }),
  update: (id, form) =>
    updateEstate(id as string, {
      estate_name: form.estate_name,
      estate_type: form.estate_type,
      estate_address: form.estate_address,
      asset_id: form.asset_id,
      fx_code: form.fx_code,
      obtain_date: form.obtain_date,
      loan_id: form.loan_id ?? null,
      estate_status: form.estate_status,
      region: form.region ?? null,
      memo: form.memo ?? null,
    }),
  remove: (id) => deleteEstate(id as string),
  refetch: () => {
    if (estatesAssetId.value) return store.fetchEstates(estatesAssetId.value)
  },
  confirmDelete: (row) => ({
    title: t('otherAssets.deleteEstateTitle'),
    message: t('otherAssets.deleteEstateMsg', { name: row.estate_name }),
  }),
  onAfterDelete: (row) => {
    estateDetailsByEstate.delete(row.estate_id)
  },
})

const estateLoanIdProxy = computed<string>({
  get: () => estateForm.value.loan_id ?? '',
  set: (v) => {
    estateForm.value.loan_id = v.trim() ? v.trim() : null
  },
})

const estateMemoProxy = computed<string>({
  get: () => estateForm.value.memo ?? '',
  set: (v) => {
    estateForm.value.memo = v ? v : null
  },
})

const estateFormObtainDate = useDateStringModel(
  () => estateForm.value.obtain_date,
  (date) => {
    estateForm.value.obtain_date = date ?? ''
  },
)

const estateDetailsByEstate = shallowReactive(new Map<string, EstateJournal[]>())
const estateDetailsLoadingByEstate = shallowReactive(new Map<string, boolean>())

async function fetchEstateDetails(estateId: string) {
  estateDetailsLoadingByEstate.set(estateId, true)
  try {
    const details = await getEstateDetails(estateId)
    estateDetailsByEstate.set(estateId, details)
  } finally {
    estateDetailsLoadingByEstate.set(estateId, false)
  }
}

function onEstateExpandChange(row: EstateAsset, expanded: EstateAsset[]) {
  const isExpanded = expanded.some((r) => r.estate_id === row.estate_id)
  if (isExpanded && !estateDetailsByEstate.has(row.estate_id)) {
    void fetchEstateDetails(row.estate_id)
  }
}

interface EstateDetailFormState extends EstateJournalCreate {
  distinct_number?: number
}

const estateDetailFormRef = ref<FormInstance>()
const estateDetailParent = ref<EstateAsset | null>(null)

function emptyEstateDetailForm(estateId: string): EstateDetailFormState {
  return {
    estate_id: estateId,
    estate_excute_type: 'tax',
    excute_price: 0,
    excute_date: todayYyyymmdd(),
    memo: null,
  }
}

const estateDetailFormRules = computed(() => estateDetailFullRules(t))

function estateDetailPayload(form: EstateDetailFormState): EstateJournalCreate {
  return {
    estate_id: form.estate_id,
    estate_excute_type: form.estate_excute_type,
    excute_price: Number(form.excute_price ?? 0),
    excute_date: form.excute_date,
    memo: form.memo || null,
  }
}

const {
  dialogVisible: estateDetailDialogVisible,
  formMode: estateDetailFormMode,
  submitting: estateDetailSubmitting,
  form: estateDetailForm,
  openCreate: openCreateEstateDetailBase,
  openEdit: openEditEstateDetailBase,
  submit: submitEstateDetail,
  remove: removeEstateDetailBase,
} = useCrudDialog<EstateJournal, EstateDetailFormState>({
  formRef: estateDetailFormRef,
  emptyForm: () => emptyEstateDetailForm(estateDetailParent.value?.estate_id ?? ''),
  toForm: (detail) => ({
    distinct_number: detail.distinct_number,
    estate_id: estateDetailParent.value!.estate_id,
    estate_excute_type: detail.estate_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }),
  getId: (detail) => detail.distinct_number,
  create: (form) => createEstateDetail(form.estate_id, estateDetailPayload(form)),
  update: (id, form) => updateEstateDetail(id as number, estateDetailPayload(form)),
  remove: (id) => deleteEstateDetail(id as number),
  refetch: () => fetchEstateDetails(estateDetailParent.value!.estate_id),
  confirmDelete: (detail) => ({
    title: t('otherAssets.deleteEstateDetailTitle'),
    message: t('otherAssets.deleteEstateDetailMsg', {
      date: detail.excute_date,
      type: detail.estate_excute_type,
    }),
  }),
})

function openCreateEstateDetail(estate: EstateAsset) {
  estateDetailParent.value = estate
  openCreateEstateDetailBase()
}

function openEditEstateDetail(estate: EstateAsset, detail: EstateJournal) {
  estateDetailParent.value = estate
  openEditEstateDetailBase(detail)
}

function handleDeleteEstateDetail(estate: EstateAsset, detail: EstateJournal) {
  estateDetailParent.value = estate
  return removeEstateDetailBase(detail)
}

// ─── Insurances ─────────────────────────────────────────────────────────────
const insuranceCategoryOptions = computed(() =>
  [...store.otherAssets]
    .filter((a) => a.asset_type.toLowerCase() === 'insurance' && a.in_use === 'Y')
    .sort((a, b) => a.asset_index - b.asset_index),
)

const insurancesAssetId = ref<string>('')

watch(insuranceCategoryOptions, (options) => {
  if (!insurancesAssetId.value && options.length > 0) {
    insurancesAssetId.value = options[0]!.asset_id
  }
})

watch(insurancesAssetId, (assetId) => {
  if (assetId) void store.fetchInsurances(assetId)
})

const insuranceFormRef = ref<FormInstance>()

function emptyInsuranceForm(): InsuranceAssetCreate {
  return {
    insurance_id: '',
    insurance_name: '',
    asset_id: insurancesAssetId.value,
    in_account: '',
    out_account: '',
    start_date: todayYyyymmdd(),
    end_date: dayjs().add(1, 'year').format('YYYYMMDD'),
    pay_type: 'annual',
    pay_day: '',
    expected_spend: 0,
    has_closed: 'N',
  }
}

const insuranceFormRules = computed<FormRules>(() => ({
  insurance_id: [{ required: true, message: t('otherAssets.enterInsuranceId'), trigger: 'blur' }],
  insurance_name: [{ required: true, message: t('otherAssets.enterName'), trigger: 'blur' }],
  in_account: [{ required: true, message: t('otherAssets.enterInAccount'), trigger: 'blur' }],
  out_account: [{ required: true, message: t('otherAssets.enterOutAccount'), trigger: 'blur' }],
  start_date: [{ required: true, message: t('otherAssets.pickStartDate'), trigger: 'change' }],
  end_date: [{ required: true, message: t('otherAssets.pickEndDate'), trigger: 'change' }],
  pay_type: [{ required: true, message: t('otherAssets.enterPayType'), trigger: 'blur' }],
  pay_day: [{ required: true, message: t('otherAssets.enterPayDay'), trigger: 'blur' }],
  expected_spend: [{ required: true, message: t('otherAssets.enterExpectedPremium'), trigger: 'blur' }],
  has_closed: [{ required: true, message: t('otherAssets.pickClosedStatus'), trigger: 'change' }],
}))

const {
  dialogVisible: insuranceDialogVisible,
  formMode: insuranceFormMode,
  submitting: insuranceSubmitting,
  form: insuranceForm,
  openCreate: openCreateInsurance,
  openEdit: openEditInsurance,
  submit: submitInsurance,
  remove: handleDeleteInsurance,
} = useCrudDialog<InsuranceAsset, InsuranceAssetCreate>({
  formRef: insuranceFormRef,
  emptyForm: emptyInsuranceForm,
  toForm: (row) => ({
    insurance_id: row.insurance_id,
    insurance_name: row.insurance_name,
    asset_id: row.asset_id,
    in_account: row.in_account,
    out_account: row.out_account,
    start_date: row.start_date,
    end_date: row.end_date,
    pay_type: row.pay_type,
    pay_day: row.pay_day,
    expected_spend: row.expected_spend,
    has_closed: row.has_closed,
  }),
  getId: (row) => row.insurance_id,
  create: (form) => createInsurance({ ...form }),
  update: (id, form) => {
    const { insurance_id, ...rest } = form
    void insurance_id
    return updateInsurance(id as string, rest)
  },
  remove: (id) => deleteInsurance(id as string),
  refetch: () => {
    if (insurancesAssetId.value) return store.fetchInsurances(insurancesAssetId.value)
  },
  confirmDelete: (row) => ({
    title: t('otherAssets.deleteInsuranceTitle'),
    message: t('otherAssets.deleteInsuranceMsg', { name: row.insurance_name }),
  }),
  onAfterDelete: (row) => {
    insuranceDetailsByPolicy.delete(row.insurance_id)
  },
})

const insuranceFormStartDate = useDateStringModel(
  () => insuranceForm.value.start_date,
  (date) => {
    insuranceForm.value.start_date = date ?? ''
  },
)

const insuranceFormEndDate = useDateStringModel(
  () => insuranceForm.value.end_date,
  (date) => {
    insuranceForm.value.end_date = date ?? ''
  },
)

const insuranceDetailsByPolicy = shallowReactive(new Map<string, InsuranceJournal[]>())
const insuranceDetailsLoadingByPolicy = shallowReactive(new Map<string, boolean>())

async function fetchInsuranceDetails(insuranceId: string) {
  insuranceDetailsLoadingByPolicy.set(insuranceId, true)
  try {
    const details = await getInsuranceDetails(insuranceId)
    insuranceDetailsByPolicy.set(insuranceId, details)
  } finally {
    insuranceDetailsLoadingByPolicy.set(insuranceId, false)
  }
}

function onInsuranceExpandChange(row: InsuranceAsset, expanded: InsuranceAsset[]) {
  const isExpanded = expanded.some((r) => r.insurance_id === row.insurance_id)
  if (isExpanded && !insuranceDetailsByPolicy.has(row.insurance_id)) {
    void fetchInsuranceDetails(row.insurance_id)
  }
}

interface InsuranceDetailFormState extends InsuranceJournalCreate {
  distinct_number?: number
}

const insuranceDetailFormRef = ref<FormInstance>()
const insuranceDetailParent = ref<InsuranceAsset | null>(null)

function emptyInsuranceDetailForm(insuranceId: string): InsuranceDetailFormState {
  return {
    insurance_id: insuranceId,
    insurance_excute_type: 'pay',
    excute_price: 0,
    excute_date: todayYyyymmdd(),
    memo: null,
  }
}

const insuranceDetailFormRules = computed(() => insuranceDetailFullRules(t))

function insuranceDetailPayload(form: InsuranceDetailFormState): InsuranceJournalCreate {
  return {
    insurance_id: form.insurance_id,
    insurance_excute_type: form.insurance_excute_type,
    excute_price: Number(form.excute_price ?? 0),
    excute_date: form.excute_date,
    memo: form.memo || null,
  }
}

const {
  dialogVisible: insuranceDetailDialogVisible,
  formMode: insuranceDetailFormMode,
  submitting: insuranceDetailSubmitting,
  form: insuranceDetailForm,
  openCreate: openCreateInsuranceDetailBase,
  openEdit: openEditInsuranceDetailBase,
  submit: submitInsuranceDetail,
  remove: removeInsuranceDetailBase,
} = useCrudDialog<InsuranceJournal, InsuranceDetailFormState>({
  formRef: insuranceDetailFormRef,
  emptyForm: () => emptyInsuranceDetailForm(insuranceDetailParent.value?.insurance_id ?? ''),
  toForm: (detail) => ({
    distinct_number: detail.distinct_number,
    insurance_id: insuranceDetailParent.value!.insurance_id,
    insurance_excute_type: detail.insurance_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }),
  getId: (detail) => detail.distinct_number,
  create: (form) => createInsuranceDetail(form.insurance_id, insuranceDetailPayload(form)),
  update: (id, form) => updateInsuranceDetail(id as number, insuranceDetailPayload(form)),
  remove: (id) => deleteInsuranceDetail(id as number),
  refetch: () => fetchInsuranceDetails(insuranceDetailParent.value!.insurance_id),
  confirmDelete: (detail) => ({
    title: t('otherAssets.deleteInsuranceDetailTitle'),
    message: t('otherAssets.deleteInsuranceDetailMsg', {
      date: detail.excute_date,
      type: detail.insurance_excute_type,
    }),
  }),
})

function openCreateInsuranceDetail(insurance: InsuranceAsset) {
  insuranceDetailParent.value = insurance
  openCreateInsuranceDetailBase()
}

function openEditInsuranceDetail(insurance: InsuranceAsset, detail: InsuranceJournal) {
  insuranceDetailParent.value = insurance
  openEditInsuranceDetailBase(detail)
}

function handleDeleteInsuranceDetail(insurance: InsuranceAsset, detail: InsuranceJournal) {
  insuranceDetailParent.value = insurance
  return removeInsuranceDetailBase(detail)
}

// ─── Loans ──────────────────────────────────────────────────────────────────
const loanFormRef = ref<FormInstance>()

function emptyLoanForm(): LoanAssetCreate {
  return {
    loan_id: '',
    loan_name: '',
    loan_type: '',
    account_id: '',
    account_name: '',
    interest_rate: 0,
    period: 12,
    apply_date: todayYyyymmdd(),
    grace_expire_date: null,
    pay_day: 1,
    amount: 0,
    repayed: 0,
    loan_index: 0,
  }
}

const loanFormRules = computed<FormRules>(() => ({
  loan_id: [{ required: true, message: t('otherAssets.enterLoanId'), trigger: 'blur' }],
  loan_name: [{ required: true, message: t('otherAssets.enterName'), trigger: 'blur' }],
  loan_type: [{ required: true, message: t('otherAssets.enterType'), trigger: 'blur' }],
  account_id: [{ required: true, message: t('validation.enterAccountId'), trigger: 'blur' }],
  account_name: [{ required: true, message: t('validation.enterAccountName'), trigger: 'blur' }],
  interest_rate: [{ required: true, message: t('otherAssets.enterAnnualRate'), trigger: 'blur' }],
  period: [{ required: true, message: t('otherAssets.enterPeriod'), trigger: 'blur' }],
  apply_date: [{ required: true, message: t('otherAssets.pickApplyDate'), trigger: 'change' }],
  pay_day: [{ required: true, message: t('otherAssets.enterPayDay'), trigger: 'blur' }],
  amount: [{ required: true, message: t('otherAssets.enterPrincipal'), trigger: 'blur' }],
  repayed: [{ required: true, message: t('otherAssets.enterRepayed'), trigger: 'blur' }],
  loan_index: [{ required: true, message: t('otherAssets.enterSortIndex'), trigger: 'blur' }],
}))

const {
  dialogVisible: loanDialogVisible,
  formMode: loanFormMode,
  submitting: loanSubmitting,
  form: loanForm,
  openCreate: openCreateLoan,
  openEdit: openEditLoan,
  submit: submitLoan,
  remove: handleDeleteLoan,
} = useCrudDialog<LoanAsset, LoanAssetCreate>({
  formRef: loanFormRef,
  emptyForm: emptyLoanForm,
  toForm: (row) => ({
    loan_id: row.loan_id,
    loan_name: row.loan_name,
    loan_type: row.loan_type,
    account_id: row.account_id,
    account_name: row.account_name,
    interest_rate: row.interest_rate,
    period: row.period,
    apply_date: row.apply_date,
    grace_expire_date: row.grace_expire_date ?? null,
    pay_day: row.pay_day,
    amount: row.amount,
    repayed: row.repayed,
    loan_index: row.loan_index,
  }),
  getId: (row) => row.loan_id,
  create: (form) => createLoan({ ...form }),
  update: (id, form) => {
    const { loan_id, ...rest } = form
    void loan_id
    return updateLoan(id as string, rest)
  },
  remove: (id) => deleteLoan(id as string),
  refetch: () => store.fetchLoans(),
  confirmDelete: (row) => ({
    title: t('otherAssets.deleteLoanTitle'),
    message: t('otherAssets.deleteLoanMsg', { name: row.loan_name }),
  }),
  onAfterDelete: (row) => {
    loanDetailsByLoan.delete(row.loan_id)
  },
})

const loanFormApplyDate = useDateStringModel(
  () => loanForm.value.apply_date,
  (date) => {
    loanForm.value.apply_date = date ?? ''
  },
)

// Cleared grace date stays null (optional field), unlike the ''-coerced ones.
const loanFormGraceDate = useDateStringModel(
  () => loanForm.value.grace_expire_date,
  (date) => {
    loanForm.value.grace_expire_date = date
  },
)

const loanDetailsByLoan = shallowReactive(new Map<string, LoanJournal[]>())
const loanDetailsLoadingByLoan = shallowReactive(new Map<string, boolean>())

async function fetchLoanDetails(loanId: string) {
  loanDetailsLoadingByLoan.set(loanId, true)
  try {
    const details = await getLoanDetails(loanId)
    loanDetailsByLoan.set(loanId, details)
  } finally {
    loanDetailsLoadingByLoan.set(loanId, false)
  }
}

function onLoanExpandChange(row: LoanAsset, expanded: LoanAsset[]) {
  const isExpanded = expanded.some((r) => r.loan_id === row.loan_id)
  if (isExpanded && !loanDetailsByLoan.has(row.loan_id)) {
    void fetchLoanDetails(row.loan_id)
  }
}

interface LoanDetailFormState extends LoanJournalCreate {
  distinct_number?: number
}

const loanDetailFormRef = ref<FormInstance>()
const loanDetailParent = ref<LoanAsset | null>(null)

function emptyLoanDetailForm(loanId: string): LoanDetailFormState {
  return {
    loan_id: loanId,
    loan_excute_type: 'principal',
    excute_price: 0,
    excute_date: todayYyyymmdd(),
    memo: null,
  }
}

const loanDetailFormRules = computed<FormRules>(() => ({
  excute_date: [{ required: true, message: t('validation.pickDate'), trigger: 'change' }],
  loan_excute_type: [{ required: true, message: t('validation.pickType'), trigger: 'change' }],
  excute_price: [{ required: true, message: t('validation.enterAmount'), trigger: 'blur' }],
}))

function loanDetailPayload(form: LoanDetailFormState): LoanJournalCreate {
  return {
    loan_id: form.loan_id,
    loan_excute_type: form.loan_excute_type,
    excute_price: Number(form.excute_price ?? 0),
    excute_date: form.excute_date,
    memo: form.memo ?? null,
  }
}

const {
  dialogVisible: loanDetailDialogVisible,
  formMode: loanDetailFormMode,
  submitting: loanDetailSubmitting,
  form: loanDetailForm,
  openCreate: openCreateLoanDetailBase,
  openEdit: openEditLoanDetailBase,
  submit: submitLoanDetail,
  remove: removeLoanDetailBase,
} = useCrudDialog<LoanJournal, LoanDetailFormState>({
  formRef: loanDetailFormRef,
  emptyForm: () => emptyLoanDetailForm(loanDetailParent.value?.loan_id ?? ''),
  toForm: (detail) => ({
    distinct_number: detail.distinct_number,
    loan_id: loanDetailParent.value!.loan_id,
    loan_excute_type: detail.loan_excute_type,
    excute_price: detail.excute_price,
    excute_date: detail.excute_date,
    memo: detail.memo ?? null,
  }),
  getId: (detail) => detail.distinct_number,
  create: (form) => createLoanDetail(form.loan_id, loanDetailPayload(form)),
  update: (id, form) => updateLoanDetail(id as number, loanDetailPayload(form)),
  remove: (id) => deleteLoanDetail(id as number),
  refetch: () => fetchLoanDetails(loanDetailParent.value!.loan_id),
  confirmDelete: (detail) => ({
    title: t('otherAssets.deleteLoanDetailTitle'),
    message: t('otherAssets.deleteLoanDetailMsg', {
      date: detail.excute_date,
      type: detail.loan_excute_type,
    }),
  }),
})

const loanDetailMemoProxy = computed<string>({
  get: () => loanDetailForm.value.memo ?? '',
  set: (v) => {
    loanDetailForm.value.memo = v ? v : null
  },
})

const loanDetailFormDate = useDateStringModel(
  () => loanDetailForm.value.excute_date,
  (date) => {
    loanDetailForm.value.excute_date = date ?? ''
  },
)

function openCreateLoanDetail(loan: LoanAsset) {
  loanDetailParent.value = loan
  openCreateLoanDetailBase()
}

function openEditLoanDetail(loan: LoanAsset, detail: LoanJournal) {
  loanDetailParent.value = loan
  openEditLoanDetailBase(detail)
}

function handleDeleteLoanDetail(loan: LoanAsset, detail: LoanJournal) {
  loanDetailParent.value = loan
  return removeLoanDetailBase(detail)
}

// ─── Other-Assets ───────────────────────────────────────────────────────────
const otherAssetsSorted = computed(() =>
  [...store.otherAssets].sort((a, b) => a.asset_index - b.asset_index),
)

const otherAssetFormRef = ref<FormInstance>()

function emptyOtherAssetForm(): OtherAssetCreate {
  return {
    asset_id: '',
    asset_name: '',
    asset_type: 'stock',
    in_use: 'Y',
    asset_index: undefined,
  }
}

const otherAssetFormRules = computed<FormRules>(() => ({
  asset_id: [{ required: true, message: t('otherAssets.enterId'), trigger: 'blur' }],
  asset_name: [{ required: true, message: t('otherAssets.enterName'), trigger: 'blur' }],
  asset_type: [{ required: true, message: t('validation.pickType'), trigger: 'change' }],
  in_use: [{ required: true, message: t('otherAssets.pickEnabledStatus'), trigger: 'change' }],
}))

const {
  dialogVisible: otherAssetDialogVisible,
  formMode: otherAssetFormMode,
  submitting: otherAssetSubmitting,
  form: otherAssetForm,
  openCreate: openCreateOtherAsset,
  openEdit: openEditOtherAsset,
  submit: submitOtherAsset,
  remove: handleDeleteOtherAsset,
} = useCrudDialog<OtherAsset, OtherAssetCreate>({
  formRef: otherAssetFormRef,
  emptyForm: emptyOtherAssetForm,
  toForm: (row) => ({
    asset_id: row.asset_id,
    asset_name: row.asset_name,
    asset_type: row.asset_type,
    in_use: row.in_use,
    asset_index: row.asset_index,
  }),
  getId: (row) => row.asset_id,
  create: (form) => createOtherAsset({ ...form }),
  update: (id, form) => {
    const { asset_id, ...rest } = form
    void asset_id
    return updateOtherAsset(id as string, rest)
  },
  remove: (id) => deleteOtherAsset(id as string),
  refetch: () => store.fetchOtherAssets(),
  confirmDelete: (row) => ({
    title: t('otherAssets.deleteCategoryTitle'),
    message: t('otherAssets.deleteCategoryMsg', { name: row.asset_name, id: row.asset_id }),
  }),
})

const otherAssetIndexProxy = computed<number | undefined>({
  get: () => otherAssetForm.value.asset_index,
  set: (v) => {
    otherAssetForm.value.asset_index = typeof v === 'number' ? v : undefined
  },
})

// ─── Lifecycle ──────────────────────────────────────────────────────────────
onMounted(() => {
  void store.fetchOtherAssets()
  void store.fetchLoans()
  void settingStore.fetchStockCategories()
})
</script>
