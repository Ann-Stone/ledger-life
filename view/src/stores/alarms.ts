import { defineStore } from 'pinia'
import { computed } from 'vue'
import dayjs from 'dayjs'
import { useFetchState } from '@/composables/useFetchState'
import { getDashboardAlarms } from '@/api/dashboard'
import type { AlarmType, DashboardAlarm } from '@/types/models'

export type Urgency = 'this_week' | 'this_month' | 'later'

export interface AlarmWithMeta extends DashboardAlarm {
  daysUntil: number       // negative = overdue
  urgency: Urgency
  displayDate: string     // M/D
  recurrence: AlarmType
}

function parseAlarmDate(yyyymmdd: string): dayjs.Dayjs {
  return dayjs(yyyymmdd, 'YYYYMMDD')
}

function classify(daysUntil: number): Urgency {
  if (daysUntil <= 7) return 'this_week'
  if (daysUntil <= 30) return 'this_month'
  return 'later'
}

export const useAlarmStore = defineStore('alarms', () => {
  const alarmsState = useFetchState(() => getDashboardAlarms(), [] as DashboardAlarm[])
  const alarms = alarmsState.data

  // Decorated + sorted ascending by date.
  const decorated = computed<AlarmWithMeta[]>(() => {
    const now = dayjs().startOf('day')
    return alarms.value
      .map((a) => {
        const d = parseAlarmDate(a.date)
        const daysUntil = d.diff(now, 'day')
        return {
          ...a,
          daysUntil,
          urgency: classify(daysUntil),
          displayDate: d.format('M/D'),
          recurrence: a.alarm_type,
        }
      })
      .sort((a, b) => a.daysUntil - b.daysUntil)
  })

  // Most urgent alarm (smallest daysUntil — including overdue).
  const mostUrgent = computed<AlarmWithMeta | null>(
    () => decorated.value[0] ?? null,
  )

  const grouped = computed(() => ({
    this_week: decorated.value.filter((a) => a.urgency === 'this_week'),
    this_month: decorated.value.filter((a) => a.urgency === 'this_month'),
    later: decorated.value.filter((a) => a.urgency === 'later'),
  }))

  return {
    alarms,
    loading: alarmsState.loading,
    fetchAlarms: alarmsState.fetch,
    decorated,
    mostUrgent,
    grouped,
  }
})
