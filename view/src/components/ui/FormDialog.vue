<template>
  <el-dialog
    :model-value="modelValue"
    :title="title"
    :width="width"
    :close-on-click-modal="false"
    append-to-body
    @update:model-value="(v: boolean) => emit('update:modelValue', v)"
    @close="onCancel"
  >
    <slot />

    <template #footer>
      <slot name="footer">
        <el-button @click="onCancel">{{ cancelLabel }}</el-button>
        <el-button type="primary" :loading="loading" @click="onSubmit">
          {{ submitLabel }}
        </el-button>
      </slot>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(
  defineProps<{
    modelValue: boolean
    title: string
    loading?: boolean
    submitText?: string
    cancelText?: string
    width?: string
  }>(),
  {
    loading: false,
    width: '520px',
  },
)

const emit = defineEmits<{
  (e: 'update:modelValue', value: boolean): void
  (e: 'submit'): void
  (e: 'cancel'): void
}>()

const { t } = useI18n()

// Default to the shared common.* labels; callers can still override.
const submitLabel = computed(() => props.submitText ?? t('common.submit'))
const cancelLabel = computed(() => props.cancelText ?? t('common.cancel'))

const onSubmit = () => emit('submit')
const onCancel = () => {
  emit('cancel')
  emit('update:modelValue', false)
}
</script>
