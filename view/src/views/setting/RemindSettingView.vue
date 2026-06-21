<template>
  <div class="flex flex-col gap-6">
    <PageHeader :title="t('settingRemind.title')" :subtitle="t('settingRemind.subtitle')">
      <template #actions>
        <el-button type="primary" :icon="PlusIcon" @click="openCreate">
          {{ t('settingRemind.addReminder') }}
        </el-button>
      </template>
    </PageHeader>

    <DataListCard :title="t('settingRemind.listTitle')">
      <div class="p-4">
        <el-table
          :data="store.alarms"
          v-loading="store.alarmsLoading"
          stripe
          :empty-text="t('settingRemind.emptyText')"
        >
          <el-table-column :label="t('settingRemind.colRecur')" min-width="100">
            <template #default="{ row }">
              <span
                class="text-xs font-semibold px-2 py-0.5 rounded bg-on-surface-variant/10 text-on-surface-variant"
              >
                🔁 {{ row.alarm_type === 'Y' ? t('settingRemind.recurYearly') : t('settingRemind.recurMonthly') }}
              </span>
            </template>
          </el-table-column>
          <el-table-column :label="t('settingRemind.colAnchor')" min-width="140">
            <template #default="{ row }">{{ formatRecurAnchor(row) }}</template>
          </el-table-column>
          <el-table-column prop="content" :label="t('settingRemind.colContent')" min-width="260" />
          <el-table-column :label="t('settingRemind.colDueDate')" min-width="140">
            <template #default="{ row }">{{ formatDate(row.due_date) }}</template>
          </el-table-column>
          <el-table-column :label="t('common.actions')" width="160" fixed="right">
            <template #default="{ row }">
              <el-button link type="primary" @click="openEdit(row)">{{ t('common.edit') }}</el-button>
              <el-button link type="danger" @click="handleDelete(row)">{{ t('common.delete') }}</el-button>
            </template>
          </el-table-column>
        </el-table>
      </div>
    </DataListCard>

    <FormDialog
      v-model="alarmDialogVisible"
      :title="formMode === 'create' ? t('settingRemind.addReminder') : t('settingRemind.editReminder')"
      :loading="submitting"
      width="520px"
      @submit="submitAlarm"
    >
      <el-form
        ref="alarmFormRef"
        :model="alarmForm"
        :rules="alarmFormRules"
        label-width="100px"
      >
        <el-form-item :label="t('settingRemind.colRecur')" prop="alarm_type">
          <el-select v-model="alarmForm.alarm_type" :placeholder="t('settingRemind.selectRecur')" style="width: 100%">
            <el-option :label="t('settingRemind.optionYearly')" value="Y" />
            <el-option :label="t('settingRemind.optionMonthly')" value="M" />
          </el-select>
        </el-form-item>
        <el-form-item :label="anchorLabel" prop="alarm_date">
          <el-input
            v-model="alarmForm.alarm_date"
            :placeholder="anchorPlaceholder"
            :maxlength="alarmForm.alarm_type === 'Y' ? 4 : 2"
          />
        </el-form-item>
        <el-form-item :label="t('settingRemind.colContent')" prop="content">
          <el-input v-model="alarmForm.content" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item :label="t('settingRemind.colDueDate')">
          <el-date-picker
            v-model="dueDateModel"
            type="date"
            value-format="YYYYMMDD"
            :placeholder="t('settingRemind.dueDatePlaceholder')"
            clearable
            style="width: 100%"
          />
        </el-form-item>
      </el-form>
    </FormDialog>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus as PlusIcon } from '@element-plus/icons-vue'
import dayjs from 'dayjs'
import PageHeader from '@/components/ui/PageHeader.vue'
import DataListCard from '@/components/ui/DataListCard.vue'
import FormDialog from '@/components/ui/FormDialog.vue'
import { useConfirm } from '@/composables/useConfirm'
import { useSettingStore } from '@/stores/setting'
import { createAlarm, updateAlarm, deleteAlarm } from '@/api/setting'
import type { Alarm, AlarmCreate, AlarmType } from '@/types/models'

const store = useSettingStore()
const confirm = useConfirm()
const { t } = useI18n()

onMounted(() => {
  void store.fetchAlarms()
})

function formatDate(value: string | null | undefined): string {
  if (!value) return '—'
  const parsed = dayjs(value, 'YYYYMMDD')
  return parsed.isValid() ? parsed.format('YYYY/MM/DD') : value
}

function formatRecurAnchor(row: Alarm): string {
  if (row.alarm_type === 'Y' && row.alarm_date.length === 4) {
    return t('settingRemind.recurAnchorYearly', {
      date: `${row.alarm_date.slice(0, 2)}/${row.alarm_date.slice(2)}`,
    })
  }
  if (row.alarm_type === 'M' && row.alarm_date.length === 2) {
    return t('settingRemind.recurAnchorMonthly', { day: row.alarm_date })
  }
  return row.alarm_date
}

const alarmDialogVisible = ref(false)
const formMode = ref<'create' | 'edit'>('create')
const submitting = ref(false)
const alarmFormRef = ref<FormInstance>()
const editingAlarmId = ref<number | null>(null)

function emptyAlarmForm(): AlarmCreate {
  return {
    alarm_type: 'Y',
    alarm_date: '',
    content: '',
    due_date: null,
  }
}

const alarmForm = ref<AlarmCreate>(emptyAlarmForm())

const dueDateModel = computed<string>({
  get: () => alarmForm.value.due_date ?? '',
  set: (v) => {
    alarmForm.value.due_date = v ? v : null
  },
})

const anchorLabel = computed(() =>
  alarmForm.value.alarm_type === 'Y'
    ? t('settingRemind.anchorLabelYearly')
    : t('settingRemind.anchorLabelMonthly'),
)

const anchorPlaceholder = computed(() =>
  alarmForm.value.alarm_type === 'Y'
    ? t('settingRemind.anchorPlaceholderYearly')
    : t('settingRemind.anchorPlaceholderMonthly'),
)

const alarmFormRules = computed<FormRules>(() => ({
  alarm_type: [{ required: true, message: t('settingRemind.pickRecur'), trigger: 'change' }],
  alarm_date: [
    { required: true, message: t('settingRemind.enterAnchor'), trigger: 'blur' },
    {
      validator: (_rule: unknown, value: string, callback: (error?: Error) => void) => {
        const type: AlarmType = alarmForm.value.alarm_type as AlarmType
        if (type === 'Y') {
          if (!/^\d{4}$/.test(value))
            return callback(new Error(t('settingRemind.anchorYearlyFormat')))
          const mm = Number(value.slice(0, 2))
          const dd = Number(value.slice(2))
          if (mm < 1 || mm > 12) return callback(new Error(t('settingRemind.monthRange')))
          if (dd < 1 || dd > 31) return callback(new Error(t('settingRemind.dayRange')))
        } else {
          if (!/^\d{2}$/.test(value))
            return callback(new Error(t('settingRemind.anchorMonthlyFormat')))
          const dd = Number(value)
          if (dd < 1 || dd > 31) return callback(new Error(t('settingRemind.dayRange')))
        }
        callback()
      },
      trigger: 'blur',
    },
  ],
  content: [{ required: true, message: t('validation.enterContent'), trigger: 'blur' }],
}))

function openCreate() {
  formMode.value = 'create'
  editingAlarmId.value = null
  alarmForm.value = emptyAlarmForm()
  alarmDialogVisible.value = true
}

function openEdit(row: Alarm) {
  formMode.value = 'edit'
  editingAlarmId.value = row.alarm_id
  alarmForm.value = {
    alarm_type: row.alarm_type,
    alarm_date: row.alarm_date,
    content: row.content,
    due_date: row.due_date ?? null,
  }
  alarmDialogVisible.value = true
}

async function submitAlarm() {
  if (!alarmFormRef.value) return
  const valid = await alarmFormRef.value.validate().catch(() => false)
  if (!valid) return
  submitting.value = true
  try {
    if (formMode.value === 'create') {
      await createAlarm({ ...alarmForm.value })
      ElMessage.success(t('toast.addSuccess'))
    } else if (editingAlarmId.value !== null) {
      await updateAlarm(editingAlarmId.value, { ...alarmForm.value })
      ElMessage.success(t('toast.updateSuccess'))
    }
    alarmDialogVisible.value = false
    await store.fetchAlarms()
  } finally {
    submitting.value = false
  }
}

async function handleDelete(row: Alarm) {
  const ok = await confirm({
    title: t('settingRemind.deleteTitle'),
    message: t('settingRemind.deleteConfirm', { content: row.content }),
    type: 'warning',
  })
  if (!ok) return
  await deleteAlarm(row.alarm_id)
  ElMessage.success(t('toast.deleted'))
  await store.fetchAlarms()
}
</script>
