# Balance Sheet View — 專案重構分析文件

> 本文件為 `account-book-view` 原始專案的完整分析，作為重構到 Vue3 + TypeScript + Tailwind 新版本的依據。
> 分析日期：2026-02-27

---

## 一、原始專案技術棧

| 項目 | 原版 | 新版（目標）|
|------|------|------------|
| 框架 | Vue 2.5.17 | Vue 3.x (Composition API) |
| 語言 | JavaScript | TypeScript |
| UI 元件庫 | Element UI 2.4.11 | **Element Plus 2.x** |
| CSS 框架 | 手寫 SCSS | Tailwind CSS |
| 狀態管理 | Vuex 3 | Pinia |
| 路由 | Vue Router 3 | Vue Router 4 |
| 建置工具 | Webpack 4 | Vite |
| HTTP 客戶端 | Axios 0.18 | Axios 1.x |
| 圖表庫 | ECharts 4.1 | ECharts 5.x |
| 日期處理 | Moment.js | Day.js |

---

## 二、完整目錄結構（原始）

```
account-book-view/
├── build/                          # Webpack 建置設定（新版 Vite 不需要）
├── config/                         # 環境設定
├── src/
│   ├── api/                        # API 服務層
│   │   ├── dashboard.js
│   │   ├── global.js
│   │   ├── login.js
│   │   ├── monthlyReport/cashFlow.js
│   │   ├── otherAssets/
│   │   │   ├── estate.js
│   │   │   ├── insurance.js
│   │   │   ├── liability.js
│   │   │   └── stock.js
│   │   ├── setting/
│   │   │   ├── alarm.js
│   │   │   ├── budget.js
│   │   │   ├── initial.js
│   │   │   └── menu/ (account, code, creditCard, loan, otherAssets)
│   │   └── yearReport/balance.js
│   ├── assets/
│   │   └── commonData/             # 靜態參考資料
│   │       ├── accountData.js
│   │       ├── codeData.js
│   │       ├── creditCardData.js
│   │       ├── fxData.js
│   │       ├── global.js
│   │       ├── liability.js
│   │       └── otherAssets.js
│   ├── components/                 # 共用元件
│   │   ├── Charts/ (BarChart, PieChart, DoublePieChart, LineChart, MutiBarChart)
│   │   ├── Pagination/
│   │   ├── Breadcrumb/
│   │   └── ...其他工具型元件
│   ├── router/                     # 路由設定
│   ├── store/                      # Vuex 狀態管理
│   ├── utils/                      # 工具函式
│   └── views/                      # 頁面元件
│       ├── dashboard/
│       ├── monthlyReport/CashFlow/
│       ├── yearReport/ (BalanceSheet, Spending, Asset)
│       ├── otherAssetAndLiabilities/ (Stock, Estate, Insurance, Liability)
│       ├── setting/ (budget, initial, menu, remind)
│       └── layout/
```

---

## 三、應用程式功能清單

### 3.1 儀表板（Dashboard）
- **資產趨勢折線圖**：依月份或年份顯示各類資產餘額變化
- **提醒清單（Alarm List）**：定期支出的提醒通知
- **期間切換**：月份 / 年份模式切換
- **日期選擇器**：選擇查看的月份或年份

### 3.2 月報 — 現金流（Monthly Report / Cash Flow）
- **損益計算**：當月收入 - 支出 = 損益
- **雙層圓餅圖**：收支比例 vs 固定費用比例
- **多柱狀圖**：資產變動比較
- **支出預算表**：各類別 實際 vs 預算 對比
- **負債變動表**：各類貸款當月變動
- **股票價格更新對話框**：填入當月股票收盤價

### 3.3 年報（Year Report）
- **資產負債表（Balance Sheet）**
  - 資產明細（現金、存款、股票、不動產、保險、其他）
  - 負債明細（信用卡、貸款、其他負債）
  - 淨資產 = 總資產 - 總負債
- **年度支出分析（Spending）**：年度各類別支出比較
- **資產概覽（Asset）**：資產組成圓餅圖 + 表格

### 3.4 其他資產與負債管理（Other Assets & Liabilities）
五個子分頁，各有清單 + 新增/編輯/刪除功能：

| 分頁 | 主要欄位 |
|------|----------|
| **負債（Liability）** | 名稱、類型、利率、期數、每期金額、開始日期 |
| **股票（Stock）** | 代碼、名稱、預期投入、買入均價、賣出均價、股利、績效 |
| **不動產（Estate）** | 名稱、類型、購入價格、市值、貸款 |
| **保險（Insurance）** | 名稱、類型、保費、保額、到期日 |
| **其他資產（Other）** | 名稱、類型、金額 |

每個分頁都有詳細明細子對話框（Detail Dialog）與操作對話框（Operating Dialog）。

### 3.5 設定（Settings）
#### 選單設定（Menu）
- **現金流代碼（Cash Flow Code）**：收支類別管理，支援子代碼
- **帳戶（Account）**：銀行帳戶管理
- **信用卡（Credit Card）**：信用卡管理
- **非現金資產（Other Assets）**：資產類別設定
- **貸款（Loan）**：貸款類別設定

#### 預算設定（Budget）
- 依年份設定各類別預算
- 浮動費用預算 + 固定費用預算分開管理
- 可複製上年預算到下一年

#### 提醒設定（Remind）
- 定期支出提醒（例：每月固定費用）
- 可設定月份、金額、類別

#### 初始設定（Initial）
- 資產初始值設定（帳戶期初餘額）

---

## 四、路由結構（已定案）

> 決定：移除登入頁（個人工具不需要認證）、移除 TagsView（改用 Breadcrumb）

```
/dashboard                    → 儀表板（首頁，/ redirect 到此）
/monthly-report/cash-flow     → 月度現金流
/year-report/balance-sheet    → 資產負債表
/year-report/spending         → 年度支出
/year-report/assets           → 資產概覽
/other-assets                 → 其他資產負債（Tab 頁）
/setting/menu                 → 選單設定（Tab 頁）
/setting/budget               → 預算設定
/setting/remind               → 提醒設定
```

---

## 五、狀態管理結構（已定案）

> 決定：移除 user/permission/tagsView/global stores（無需認證與多頁籤）
> 採用 flat store 架構，每個業務領域一個 store。

```
src/stores/
  app.ts          ← useAppStore（UI 狀態：側邊欄、語言）         ✅ 已建立
  dashboard.ts    ← useDashboardStore（儀表板摘要、趨勢、提醒）
  cashFlow.ts     ← useCashFlowStore（月度現金流報表）
  yearReport.ts   ← useYearReportStore（資產負債表、年度支出、資產概覽）
  otherAssets.ts  ← useOtherAssetsStore（股票/不動產/保險/負債/其他）
  setting.ts      ← useSettingStore（帳戶/代碼/信用卡/預算/提醒）
```

---

## 六、API 端點清單

### ~~認證~~（已移除 — 個人工具無需登入）
| 方法 | 路徑 | 說明 |
|------|------|------|
| ~~POST~~ | ~~`/login/login`~~ | ~~登入~~ |
| POST | `/login/logout` | 登出 |
| GET | `/user/info` | 取得使用者資訊 |

### 儀表板
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/dashboard/summary` | 取得匯總資料 |
| GET | `/dashboard/alarms` | 取得提醒清單 |
| GET | `/dashboard/budgets` | 取得預算資料 |

### 月報現金流
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/monthlyReport/cashFlow` | 月度現金流資料 |
| POST | `/monthlyReport/stockPrice` | 更新股票月收盤價 |

### 年報
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/yearReport/balance` | 資產負債表資料 |
| GET | `/yearReport/spending` | 年度支出資料 |
| GET | `/yearReport/assets` | 資產概覽資料 |

### 其他資產負債
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET/POST/PUT/DELETE | `/otherAssets/stock` | 股票 CRUD |
| GET/POST/PUT/DELETE | `/otherAssets/estate` | 不動產 CRUD |
| GET/POST/PUT/DELETE | `/otherAssets/insurance` | 保險 CRUD |
| GET/POST/PUT/DELETE | `/otherAssets/liability` | 負債 CRUD |
| GET/POST/PUT/DELETE | `/otherAssets/other` | 其他資產 CRUD |

### 設定
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET/POST/PUT/DELETE | `/setting/account` | 帳戶管理 |
| GET/POST/PUT/DELETE | `/setting/code` | 現金流代碼 |
| GET/POST/PUT/DELETE | `/setting/creditCard` | 信用卡 |
| GET/POST/PUT/DELETE | `/setting/loan` | 貸款類別 |
| GET/POST/PUT/DELETE | `/setting/budget` | 預算設定 |
| GET/POST/PUT/DELETE | `/setting/remind` | 提醒設定 |

### 全域
| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/global/alive` | 伺服器存活檢查 |
| GET | `/global/checkData` | 資料完整性檢查 |

---

## 七、資料模型（TypeScript 型別定義參考）

```typescript
// 帳戶
interface Account {
  id: number
  name: string
  balance: number
  type: string
}

// 現金流類別代碼
interface CashFlowCode {
  id: number
  code: string
  name: string
  type: 'income' | 'expense' | 'fixed'
  subCodes?: SubCode[]
}

// 股票
interface Stock {
  id: number
  code: string
  name: string
  expectedSpend: number
  buyPrice: number
  sellPrice?: number
  quantity: number
  buyDate: string
  sellDate?: string
  dividendYield?: number
  roi?: number
  monthlyPrices?: MonthlyPrice[]
}

// 不動產
interface Estate {
  id: number
  name: string
  type: string
  purchasePrice: number
  currentValue: number
  mortgageAmount?: number
}

// 保險
interface Insurance {
  id: number
  name: string
  type: string
  premium: number
  coverage: number
  expiryDate?: string
}

// 負債
interface Liability {
  id: number
  name: string
  type: string
  interestRate: number
  totalPeriods: number
  periodAmount: number
  startDate: string
  balance: number
}

// 預算
interface Budget {
  id: number
  year: number
  codeId: number
  codeName: string
  type: 'floating' | 'fixed'
  amount: number
}

// 提醒
interface Remind {
  id: number
  name: string
  codeId: number
  amount: number
  month: number
  isPaid: boolean
}

// 月報現金流
interface CashFlowReport {
  year: number
  month: number
  income: number
  expense: number
  fixedExpense: number
  gainLoss: number
  categories: CashFlowCategory[]
  liabilityChanges: LiabilityChange[]
}

// 資產負債表
interface BalanceSheet {
  year: number
  assets: {
    cash: number
    deposit: number
    stock: number
    estate: number
    insurance: number
    other: number
    total: number
  }
  liabilities: {
    creditCard: number
    loan: number
    other: number
    total: number
  }
  netAssets: number
}
```

---

## 八、圖表元件需求

| 圖表名稱 | 類型 | 使用位置 | 資料格式 |
|----------|------|----------|----------|
| 資產趨勢圖 | Line Chart | Dashboard | `{ xBar: string[], series: [{name, data}] }` |
| 收支圓餅圖 | Double Pie Chart | 月報 | `{ inner: [{name,value}], outer: [{name,value}] }` |
| 資產變動圖 | Multi Bar Chart | 月報 | `{ xBar: string[], series: [{name, data}] }` |
| 資產組成圖 | Pie Chart | 年報/資產 | `[{ name: string, value: number }]` |
| 年度支出圖 | Bar Chart | 年報/支出 | `{ xBar: string[], series: [{name, data}] }` |

---

## 九、共用元件清單

| 元件 | 功能 | 優先順序 |
|------|------|----------|
| AppLayout | 整體版面（側邊欄+頂部+內容區） | 高 |
| Sidebar | 側邊導覽列 | 高 |
| Navbar | 頂部導覽列 | 高 |
| TagsView | 多頁籤瀏覽歷史 | 中 |
| Pagination | 分頁元件 | 高 |
| ChartLine | ECharts 折線圖 | 高 |
| ChartBar | ECharts 柱狀圖 | 高 |
| ChartPie | ECharts 圓餅圖 | 高 |
| ChartDoublePie | ECharts 雙層圓餅圖 | 高 |
| ChartMultiBar | ECharts 多系列柱狀圖 | 中 |
| DataTable | 通用資料表格 | 高 |
| FormDialog | 表單對話框 | 高 |
| MoneyDisplay | 金額顯示（正負色彩） | 高 |
| SearchFilter | 搜尋/篩選區域 | 中 |
| BreadcrumbNav | 麵包屑導覽 | 低 |
| SvgIcon | SVG 圖示 | 中 |
| LangSelect | 語言切換 | 低 |

---

## 十、UI 元件庫選擇討論

### 候選方案

#### 方案 A：Element Plus（推薦用於快速開發）
- **優點**：
  - Element UI 的 Vue3 版，API 幾乎相同，遷移成本最低
  - 功能完整（Table、Form、Dialog、DatePicker 等）
  - TypeScript 支援良好
  - 與原專案最相似，降低學習曲線
- **缺點**：
  - 與 Tailwind 有一些樣式衝突需處理
  - 外觀較為傳統

#### 方案 B：Naive UI
- **優點**：
  - 完全 TypeScript 編寫，型別支援極佳
  - Vue3 原生，輕量
  - 外觀現代
- **缺點**：
  - 社群相對較小
  - 某些複雜元件功能不如 Element Plus

#### 方案 C：Shadcn-vue（推薦用於長期維護）
- **優點**：
  - 元件程式碼直接放入專案，可完全客製化
  - 與 Tailwind 完美整合
  - 現代設計，品質高
  - 不是黑盒子，完全掌控
- **缺點**：
  - 需要較多初始設定
  - 部分複雜元件（DataPicker、Table）功能較基礎

#### 方案 D：PrimeVue
- **優點**：
  - 元件最完整，包含複雜的 DataTable、Calendar
  - 支援多種主題
- **缺點**：
  - 較重，學習曲線較陡
  - 免費版元件有限制

### 建議
依照優先考量：
- **快速重構、保持功能完整** → Element Plus + Tailwind（樣式層用 Tailwind 為主，Element Plus 負責複雜表單元件）
- **長期維護、現代化外觀** → Shadcn-vue + Tailwind（需補充 Radix Vue 提供的 primitives）
- **中間方案** → Naive UI + Tailwind

---

## 十一、桌面應用程式化討論

### 後期目標
讓使用者不需安裝 Python 環境也能使用，將後端打包進桌面應用程式。

### 候選框架

#### 方案 A：Electron（推薦）
- **優點**：
  - 成熟穩定，社群最大
  - 可執行 Python（透過 child_process 或 pyinstaller 打包 Python backend）
  - Electron Forge / Electron Builder 支援 macOS / Windows / Linux 打包
  - 與 Vite + Vue3 整合成熟（`electron-vite`）
- **缺點**：
  - 打包體積大（~100MB+）
  - 記憶體使用較高

#### 方案 B：Tauri（推薦 - 輕量）
- **優點**：
  - 體積極小（~10-30MB）
  - 使用系統 WebView，效能好
  - Rust 後端，安全性高
  - 支援 Vite + Vue3
- **缺點**：
  - Python backend 整合較複雜（需用 sidecar 機制）
  - 需要 Rust 環境建置

#### 方案 C：PyWebView
- **優點**：
  - 直接在 Python 中嵌入 WebView
  - Python backend 整合最簡單
- **缺點**：
  - 開發體驗不如 Electron/Tauri
  - macOS/Windows 外觀差異大

### 建議架構（Electron 方案）
```
desktop-app/
├── main/                    # Electron main process
│   ├── index.ts             # Electron 入口
│   └── pythonBridge.ts      # 呼叫 Python subprocess
├── renderer/                # Vue3 前端（即 balance-sheet-view）
└── python-backend/          # PyInstaller 打包的 Python backend
    └── dist/                # 打包後的可執行檔
```

---

## 十二、Git Pages Mock 資料部署計劃

### 架構
- 使用 `msw`（Mock Service Worker）或 `json-server` 靜態資料
- 建置時注入 `VITE_USE_MOCK=true` 環境變數
- Mock 資料放在 `/src/mock/` 目錄
- GitHub Actions 自動部署到 `gh-pages` branch

### Mock 資料需求
需要準備以下假資料：
1. 儀表板摘要資料（12 個月的資產趨勢）
2. 月度現金流資料（12 個月）
3. 資產負債表資料（3-5 年）
4. 股票持倉資料（5-10 筆）
5. 不動產/保險/負債資料（各 2-3 筆）
6. 帳戶資料（3-5 個帳戶）
7. 代碼/類別資料（收支類別）

---

## 十三、新專案目錄結構（已定案）

```
balance-sheet-view/
├── src/
│   ├── api/                        # API 服務層（TypeScript）
│   │   ├── dashboard.ts
│   │   ├── cashFlow.ts
│   │   ├── yearReport.ts
│   │   ├── otherAssets.ts
│   │   ├── setting.ts
│   │   └── mock/                   # Mock 攔截
│   │       ├── handlers.ts
│   │       └── data/               # Mock 資料 JSON
│   ├── components/
│   │   ├── layout/
│   │   │   ├── AppLayout.vue       ✅
│   │   │   ├── Sidebar.vue         ✅
│   │   │   ├── SidebarContent.vue  ✅
│   │   │   └── Navbar.vue          ✅
│   │   ├── charts/
│   │   │   ├── LineChart.vue
│   │   │   ├── BarChart.vue
│   │   │   ├── PieChart.vue
│   │   │   ├── DoublePieChart.vue
│   │   │   └── MultiBarChart.vue
│   │   └── ui/                     # 共用 UI 元件
│   │       ├── MoneyDisplay.vue
│   │       ├── Pagination.vue
│   │       ├── FormDialog.vue
│   │       └── SearchFilter.vue
│   ├── composables/                # Vue3 Composition API hooks
│   │   ├── useChart.ts
│   │   └── useTable.ts
│   ├── stores/                     # Pinia stores
│   │   ├── app.ts                  ✅
│   │   ├── dashboard.ts
│   │   ├── cashFlow.ts
│   │   ├── yearReport.ts
│   │   ├── otherAssets.ts
│   │   └── setting.ts
│   ├── router/
│   │   └── index.ts                ✅
│   ├── types/
│   │   └── models.ts               ✅
│   ├── utils/
│   │   ├── currency.ts             ✅
│   │   ├── date.ts                 ✅
│   │   └── request.ts              ✅
│   ├── views/
│   │   ├── DashboardView.vue       ✅ (stub)
│   │   ├── monthly-report/
│   │   │   └── CashFlowView.vue    ✅ (stub)
│   │   ├── year-report/
│   │   │   ├── BalanceSheetView.vue ✅ (stub)
│   │   │   ├── SpendingView.vue    ✅ (stub)
│   │   │   └── AssetView.vue       ✅ (stub)
│   │   ├── other-assets/
│   │   │   └── OtherAssetsView.vue ✅ (stub)
│   │   ├── setting/
│   │   │   ├── MenuSettingView.vue  ✅ (stub)
│   │   │   ├── BudgetSettingView.vue ✅ (stub)
│   │   │   └── RemindSettingView.vue ✅ (stub)
│   │   └── NotFoundView.vue        ✅
│   ├── env.d.ts                    ✅ (Vite 環境變數型別)
│   ├── App.vue                     ✅
│   └── main.ts                     ✅
├── .github/
│   └── workflows/
│       └── deploy.yml              # GitHub Actions 自動部署（待建立）
├── .env.example                    ✅
├── vite.config.ts                  ✅
├── tsconfig.json                   ✅
├── package.json                    ✅
├── CLAUDE.md                       ✅ (PM + 架構師 system prompt)
├── GEMINI.md                       ✅ (實作者 + 修復 system prompt)
├── AGENTS.md                       ✅ (QA 工程師 system prompt)
└── PROJECT_ANALYSIS.md             ✅ (本文件)
```

---

## 十四、已決定事項

| # | 議題 | 決定 | 原因 |
|---|------|------|------|
| 1 | UI 元件庫 | **Element Plus 2.x + Tailwind v4** | 複雜表格/表單最穩定，AI 開發效率最高 |
| 2 | 桌面應用框架 | **Electron**（後期實施） | 社群資源多、Python backend 整合成熟 |
| 3 | 認證機制 | **移除登入頁** | 個人工具不需要認證 |
| 4 | i18n 語言 | **中文 (zh-TW) + English** | 簡化維護，只保留兩種語言 |
| 5 | TagsView | **移除，改用 Breadcrumb** | 降低複雜度，個人工具不需多頁籤 |

## 十五、AI 協作分工

| 角色 | AI | System Prompt | 職責範圍 |
|------|-----|---------------|----------|
| PM + 架構師 | Claude | `CLAUDE.md` | 架構設計、複雜功能、需求分析、委派決策 |
| 主要實作者 | Gemini | `GEMINI.md` | 簡單需求、UI 調整、Bug 修復、受委派功能實作 |
| QA 工程師 | Codex | `AGENTS.md` | 功能驗證、測試、問題回報與路由分類 |

**決策流程**：所有需求與發現均先判斷是否影響架構 → 是：Claude 處理 → 否：Claude 評估後可委派 Gemini。

---

*最後更新：2026-02-27*
