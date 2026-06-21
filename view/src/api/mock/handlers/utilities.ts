import { http } from 'msw'
import { ok } from '../util'
import {
  _accountsSnapshot,
  _codesSnapshot,
  _creditCardsSnapshot,
} from './settings'
import { _stocksSnapshot } from './assets'
import type { SelectionGroup } from '@/types/models'

function groupAccounts(): SelectionGroup[] {
  const accounts = _accountsSnapshot().filter((a) => a.in_use === 'Y')
  const byType: Record<string, SelectionGroup> = {}
  for (const a of accounts) {
    const key = a.account_type || 'other'
    let group = byType[key]
    if (!group) {
      group = { label: key, options: [] }
      byType[key] = group
    }
    group.options.push({ label: a.name, value: a.account_id })
  }
  return Object.values(byType)
}

function groupCreditCards(): SelectionGroup[] {
  const cards = _creditCardsSnapshot().filter((c) => c.in_use === 'Y')
  return [{ label: 'credit_card', options: cards.map((c) => ({ label: c.card_name, value: c.credit_card_id })) }]
}

function groupCodes(parentId?: string): SelectionGroup[] {
  const codes = _codesSnapshot().filter((c) => c.in_use === 'Y')
  if (parentId) {
    const subs = codes.filter((c) => c.parent_id === parentId)
    return [{ label: parentId, options: subs.map((s) => ({ label: s.name, value: s.code_id })) }]
  }
  // Group parents by code_type
  const parents = codes.filter((c) => !c.parent_id)
  const byType: Record<string, SelectionGroup> = {}
  for (const p of parents) {
    let group = byType[p.code_type]
    if (!group) {
      group = { label: p.code_type, options: [] }
      byType[p.code_type] = group
    }
    group.options.push({ label: p.name, value: p.code_id })
  }
  return Object.values(byType)
}

export const utilitiesHandlers = [
  http.get('*/utilities/selections/accounts', () => ok(groupAccounts())),
  http.get('*/utilities/selections/credit-cards', () => ok(groupCreditCards())),
  http.get('*/utilities/selections/codes', () => ok(groupCodes())),
  http.get('*/utilities/selections/codes/:parent', ({ params }) =>
    ok(groupCodes(String(params.parent))),
  ),
  http.get('*/utilities/selections/insurances', () =>
    ok([{ label: 'insurance', options: [
      { label: '壽險 A', value: 'INS_001' },
      { label: '醫療 B', value: 'INS_002' },
      { label: '已結清 C', value: 'INS_003' },
    ] }] satisfies SelectionGroup[]),
  ),
  http.get('*/utilities/selections/estates', () =>
    ok([{ label: 'Estate', options: [
      { label: '自住公寓', value: 'EST_001' },
      { label: '出租套房', value: 'EST_002' },
    ] }] satisfies SelectionGroup[]),
  ),
  http.get('*/utilities/selections/loans', () =>
    ok([{ label: 'loan', options: [
      { label: '房貸主貸', value: 'LN_HOUSE' },
      { label: '車貸',     value: 'LN_CAR' },
      { label: '信貸',     value: 'LN_PERSONAL' },
    ] }] satisfies SelectionGroup[]),
  ),
  http.get('*/utilities/selections/other-asset-types', () =>
    ok([
      {
        label: 'Other_Asset',
        options: [
          { label: 'stock',     value: 'stock' },
          { label: 'insurance', value: 'insurance' },
          { label: 'estate',    value: 'estate' },
        ],
      },
    ] satisfies SelectionGroup[]),
  ),
  http.get('*/utilities/selections/stocks', () => {
    const stocks = _stocksSnapshot()
    const byAsset: Record<string, SelectionGroup> = {}
    for (const s of stocks) {
      let group = byAsset[s.asset_id]
      if (!group) {
        group = { label: s.asset_id, options: [] }
        byAsset[s.asset_id] = group
      }
      group.options.push({ label: `${s.stock_code} ${s.stock_name}`, value: s.stock_id })
    }
    return ok(Object.values(byAsset))
  }),
  // Import endpoints — return immediate stub success
  http.post('*/utilities/import/stock-prices', () => ok({ message: 'mock: stock-prices imported' })),
  http.post('*/utilities/import/fx-rates',     () => ok({ message: 'mock: fx-rates imported' })),
  http.post('*/utilities/import/invoices',     () => ok({
    imported: 3,
    skipped: 1,
    failed: 0,
    months: [
      { month: '202603', imported: 2, skipped: 1 },
      { month: '202604', imported: 1, skipped: 0 },
    ],
    errors: [],
  })),
]
