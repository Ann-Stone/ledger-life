// 選單設定 (Menu settings) page — accounts / categories / credit cards / stock categories.
export default {
  title: '選單設定',
  subtitle: '管理帳戶、分類與信用卡',

  // Tabs
  tabAccounts: '帳戶',
  tabCodes: '分類',
  tabCreditCards: '信用卡',
  tabStockCategories: '股票分類',

  // Accounts
  accountListTitle: '帳戶清單',
  addAccount: '新增帳戶',
  noAccounts: '尚無帳戶',
  accountId: '帳戶 ID',
  accountType: '類型',
  fxCode: '幣別',
  discount: '折扣',
  owner: '持有人',
  sortIndex: '排序',

  // Codes
  codeListTitle: '主分類 / 子分類',
  addMainCode: '新增主分類',
  noMainCodes: '尚無主分類',
  subCodesOf: '{id} 子分類',
  addSubCode: '新增子分類',
  noSubCodes: '尚無子分類',
  subCodeId: '子分類 ID',
  codeId: '分類 ID',
  annualEvent: '年度事件',
  eventTag: '事件',

  // Credit cards
  creditCardListTitle: '信用卡清單',
  addCreditCard: '新增信用卡',
  noCreditCards: '尚無信用卡',
  cardId: '卡片 ID',
  cardName: '卡名',
  cardNo: '卡號',
  lastDay: '結帳日',
  chargeDay: '扣款日',
  limitDate: '繳費日',

  // Stock categories
  stockCategoryListTitle: '股票分類',
  addStockCategory: '新增分類',
  noStockCategories: '尚無股票分類',
  categoryId: '分類 ID',

  // Dialog titles
  createCreditCard: '新增信用卡',
  editCreditCard: '編輯信用卡',
  createStockCategory: '新增股票分類',
  editStockCategory: '編輯股票分類',
  createMainCode: '新增主分類',
  editMainCode: '編輯主分類',
  createSubCode: '新增子分類',
  editSubCode: '編輯子分類',
  createAccount: '新增帳戶',
  editAccount: '編輯帳戶',

  // Form labels
  feedbackWay: '回饋方式',
  enableLabel: '啟用',
  disableLabel: '停用',
  isCalculate: '計入資產',
  yes: '是',
  no: '否',
  parentCode: '父分類',
  codeType: '類型',

  // Placeholders (translate only the Chinese hint part)
  phCardId: '如 CC-VISA-01',
  phCardNo: '如 4111-XXXX-XXXX-1111',
  phFeedbackWay: '如 cashback / mileage',
  phCodeId: '如 E01',
  phStockCategoryName: '如 成長型 / 債券 / 類現金',
  phAccountId: '如 BANK-CHASE-01',
  phAccountType: '如 BANK / CASH / INVEST',
  phFxCode: '如 TWD / USD',

  // Hints
  stockCategoryIndexHint: '分類 ID 由系統自動產生 (SC-NNN);留空排序時自動接續',
  annualEventHint: '開啟後此分類改以「全年一筆額度」編列,不分攤到 12 個月 (如過年、年節送禮)',

  // Validation messages
  enterName: '請輸入名稱',
  enterType: '請輸入類型',
  enterFxCode: '請輸入幣別',
  enterCodeId: '請輸入分類 ID',
  enterSubCodeId: '請輸入子分類 ID',
  enterCardId: '請輸入卡片 ID',
  enterCardName: '請輸入卡名',

  // Delete confirmations
  deleteAccountTitle: '刪除帳戶',
  deleteAccountMsg: '確定要刪除「{name}」?',
  deleteMainCodeTitle: '刪除主分類',
  deleteMainCodeMsg: '確定要刪除「{name}」? 子分類需先清空。',
  deleteSubCodeTitle: '刪除子分類',
  deleteSubCodeMsg: '確定要刪除「{name}」?',
  deleteCreditCardTitle: '刪除信用卡',
  deleteCreditCardMsg: '確定要刪除「{name}」?',
  deleteStockCategoryTitle: '刪除股票分類',
  deleteStockCategoryMsg: '確定要刪除「{name}」? 已被持股引用的分類請改為停用 (停用)。',
}
