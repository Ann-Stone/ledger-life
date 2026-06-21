import { settingsHandlers } from './handlers/settings'
import { monthlyReportHandlers } from './handlers/monthlyReport'
import { assetsHandlers } from './handlers/assets'
import { reportsHandlers } from './handlers/reports'
import { dashboardHandlers } from './handlers/dashboard'
import { utilitiesHandlers } from './handlers/utilities'

export const handlers = [
  ...settingsHandlers,
  ...monthlyReportHandlers,
  ...assetsHandlers,
  ...reportsHandlers,
  ...dashboardHandlers,
  ...utilitiesHandlers,
]
