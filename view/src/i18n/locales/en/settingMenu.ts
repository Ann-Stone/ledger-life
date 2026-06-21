// 選單設定 (Menu settings) page — accounts / categories / credit cards / stock categories.
export default {
  title: 'Menu Settings',
  subtitle: 'Manage accounts, categories and credit cards',

  // Tabs
  tabAccounts: 'Accounts',
  tabCodes: 'Categories',
  tabCreditCards: 'Credit Cards',
  tabStockCategories: 'Stock Categories',

  // Accounts
  accountListTitle: 'Account List',
  addAccount: 'Add Account',
  noAccounts: 'No accounts yet',
  accountId: 'Account ID',
  accountType: 'Type',
  fxCode: 'Currency',
  discount: 'Discount',
  owner: 'Owner',
  sortIndex: 'Order',

  // Codes
  codeListTitle: 'Main / Sub Categories',
  addMainCode: 'Add Main Category',
  noMainCodes: 'No main categories yet',
  subCodesOf: '{id} Sub-categories',
  addSubCode: 'Add Sub-category',
  noSubCodes: 'No sub-categories yet',
  subCodeId: 'Sub-category ID',
  codeId: 'Category ID',
  annualEvent: 'Annual Event',
  eventTag: 'Event',

  // Credit cards
  creditCardListTitle: 'Credit Card List',
  addCreditCard: 'Add Credit Card',
  noCreditCards: 'No credit cards yet',
  cardId: 'Card ID',
  cardName: 'Card Name',
  cardNo: 'Card No.',
  lastDay: 'Statement Day',
  chargeDay: 'Charge Day',
  limitDate: 'Due Day',

  // Stock categories
  stockCategoryListTitle: 'Stock Categories',
  addStockCategory: 'Add Category',
  noStockCategories: 'No stock categories yet',
  categoryId: 'Category ID',

  // Dialog titles
  createCreditCard: 'Add Credit Card',
  editCreditCard: 'Edit Credit Card',
  createStockCategory: 'Add Stock Category',
  editStockCategory: 'Edit Stock Category',
  createMainCode: 'Add Main Category',
  editMainCode: 'Edit Main Category',
  createSubCode: 'Add Sub-category',
  editSubCode: 'Edit Sub-category',
  createAccount: 'Add Account',
  editAccount: 'Edit Account',

  // Form labels
  feedbackWay: 'Reward Type',
  enableLabel: 'Enabled',
  disableLabel: 'Disabled',
  isCalculate: 'Count as Asset',
  yes: 'Yes',
  no: 'No',
  parentCode: 'Parent Category',
  codeType: 'Type',

  // Placeholders (translate only the Chinese hint part)
  phCardId: 'e.g. CC-VISA-01',
  phCardNo: 'e.g. 4111-XXXX-XXXX-1111',
  phFeedbackWay: 'e.g. cashback / mileage',
  phCodeId: 'e.g. E01',
  phStockCategoryName: 'e.g. Growth / Bond / Cash-like',
  phAccountId: 'e.g. BANK-CHASE-01',
  phAccountType: 'e.g. BANK / CASH / INVEST',
  phFxCode: 'e.g. TWD / USD',

  // Hints
  stockCategoryIndexHint: 'Category ID is auto-generated (SC-NNN); leave order blank to auto-continue',
  annualEventHint:
    'When enabled, this category uses a single full-year budget instead of being split across 12 months (e.g. New Year, holiday gifts)',

  // Validation messages
  enterName: 'Please enter a name',
  enterType: 'Please enter a type',
  enterFxCode: 'Please enter a currency',
  enterCodeId: 'Please enter a category ID',
  enterSubCodeId: 'Please enter a sub-category ID',
  enterCardId: 'Please enter a card ID',
  enterCardName: 'Please enter a card name',

  // Delete confirmations
  deleteAccountTitle: 'Delete Account',
  deleteAccountMsg: 'Delete "{name}"?',
  deleteMainCodeTitle: 'Delete Main Category',
  deleteMainCodeMsg: 'Delete "{name}"? Sub-categories must be cleared first.',
  deleteSubCodeTitle: 'Delete Sub-category',
  deleteSubCodeMsg: 'Delete "{name}"?',
  deleteCreditCardTitle: 'Delete Credit Card',
  deleteCreditCardMsg: 'Delete "{name}"?',
  deleteStockCategoryTitle: 'Delete Stock Category',
  deleteStockCategoryMsg: 'Delete "{name}"? Categories referenced by holdings should be disabled instead.',
}
