/**
 * Expenditure-composition tree builder.
 *
 * The backend already returns a two-level category → subcategory tree
 * (`ExpenditureComposition`); this maps it into the row shape `el-table`'s
 * tree mode wants, assigning unique `key`s across all rows (category codes and
 * sub codes can repeat — notably the '' un-subcategorized remainder — so keys
 * are namespaced by level and parent). A category with no children renders as a
 * flat leaf row.
 */
import type { ExpenditureComposition } from '@/types/models'

export interface ExpenditureNode {
  key: string
  label: string
  amount: number
  share: number
  type?: string // 'Fixed' | 'Floating' on category rows; absent on sub rows
  children?: ExpenditureNode[]
}

export function buildExpenditureTree(report: ExpenditureComposition): ExpenditureNode[] {
  return report.categories.map((cat) => {
    const catKey = cat.code || '_uncat_'
    const children = (cat.children ?? []).map((sub, i) => ({
      key: `sub:${catKey}:${sub.code || `_rem_${i}`}`,
      label: sub.name,
      amount: sub.amount,
      share: sub.share,
    }))
    return {
      key: `cat:${catKey}`,
      label: cat.name,
      amount: cat.amount,
      share: cat.share,
      type: cat.type,
      children: children.length ? children : undefined,
    }
  })
}
