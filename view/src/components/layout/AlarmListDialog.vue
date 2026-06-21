<template>
  <el-dialog
    :model-value="modelValue"
    :title="t('alarm.title')"
    width="520"
    @update:model-value="emit('update:modelValue', $event)"
  >
    <el-empty v-if="store.decorated.length === 0" :description="t('alarm.empty')" />
    <div v-else class="flex flex-col gap-5">
      <AlarmGroup
        v-if="store.grouped.this_week.length"
        :title="t('alarm.within7Days')"
        tone="error"
        :alarms="store.grouped.this_week"
      />
      <AlarmGroup
        v-if="store.grouped.this_month.length"
        :title="t('alarm.thisMonth')"
        tone="secondary"
        :alarms="store.grouped.this_month"
      />
      <AlarmGroup
        v-if="store.grouped.later.length"
        :title="t('alarm.later')"
        tone="muted"
        :alarms="store.grouped.later"
      />
    </div>
  </el-dialog>
</template>

<script setup lang="ts">
import { useAlarmStore } from '@/stores/alarms'
import AlarmGroup from './AlarmGroup.vue'

defineProps<{ modelValue: boolean }>()
const emit = defineEmits<{ 'update:modelValue': [value: boolean] }>()

const store = useAlarmStore()
const { t } = useI18n()
</script>
