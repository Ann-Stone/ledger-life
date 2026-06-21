import request from '@/utils/request'
import type {
  DashboardAlarm,
  DashboardBudget,
  DashboardGift,
  DashboardSummary,
  TargetSetting,
  TargetSettingCreate,
  TargetSettingUpdate,
} from '@/types/models'

export function getDashboardSummary(params: {
  type: string
  period: string  // YYYYMM-YYYYMM range
}): Promise<DashboardSummary> {
  return request.get('/dashboard/summary', { params })
}

export function getDashboardAlarms(): Promise<DashboardAlarm[]> {
  return request.get('/dashboard/alarms')
}

export function getTargets(): Promise<TargetSetting[]> {
  return request.get('/dashboard/targets')
}

export function createTarget(data: TargetSettingCreate): Promise<TargetSetting> {
  return request.post('/dashboard/targets', data)
}

export function updateTarget(targetId: string, data: TargetSettingUpdate): Promise<TargetSetting> {
  return request.put(`/dashboard/targets/${targetId}`, data)
}

export function deleteTarget(targetId: string): Promise<null> {
  return request.delete(`/dashboard/targets/${targetId}`)
}

export function getDashboardBudget(params: {
  type: string
  period: string
}): Promise<DashboardBudget> {
  return request.get('/dashboard/budget', { params })
}

export function getDashboardGifts(year: number | string): Promise<DashboardGift[]> {
  return request.get(`/dashboard/gifts/${year}`)
}
