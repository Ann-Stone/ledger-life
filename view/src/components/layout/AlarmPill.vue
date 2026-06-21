<template>
  <button
    v-if="urgent"
    type="button"
    class="flex items-center gap-2 max-w-[420px] min-w-0 px-3 py-1.5 rounded-full border cursor-pointer transition-colors"
    :class="pillClass"
    :title="`${urgent.content} · ${urgent.displayDate}`"
    @click="dialogVisible = true"
  >
    <span class="shrink-0 text-sm font-bold">{{ icon }}</span>
    <span class="shrink-0 tabular-nums text-xs font-semibold">{{ urgent.displayDate }}</span>
    <span class="truncate text-sm">{{ urgent.content }}</span>
    <span class="shrink-0 tabular-nums text-xs font-bold opacity-80">
      ({{ relativeText(urgent.daysUntil) }})
    </span>
    <span class="shrink-0 text-xs opacity-70 pl-2 border-l border-current/30">
      {{ t('alarm.viewAll', { n: store.decorated.length }) }}
    </span>
  </button>

  <AlarmListDialog v-model="dialogVisible" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { useAlarmStore } from '@/stores/alarms'
import AlarmListDialog from './AlarmListDialog.vue'

const store = useAlarmStore()
const { t } = useI18n()
const dialogVisible = ref(false)

const urgent = computed(() => store.mostUrgent)

const pillClass = computed(() => {
  const u = urgent.value
  if (!u) return ''
  if (u.urgency === 'this_week') return 'bg-error/10 text-error border-error/30 hover:bg-error/20'
  if (u.urgency === 'this_month')
    return 'bg-secondary/10 text-secondary border-secondary/30 hover:bg-secondary/20'
  return 'bg-on-surface-variant/10 text-on-surface-variant border-outline-variant hover:bg-on-surface-variant/15'
})

const icon = computed(() => {
  const u = urgent.value
  if (!u) return ''
  if (u.urgency === 'this_week') return '⚠'
  return '🔔'
})

function relativeText(days: number): string {
  if (days < 0) return t('alarm.overdue', { n: Math.abs(days) })
  if (days === 0) return t('alarm.today')
  if (days === 1) return t('alarm.tomorrow')
  return t('alarm.daysLeft', { n: days })
}
</script>
