<template>
  <!--
    Edit / delete action pair for el-table operation columns.
    Two visual variants to match the existing pages 1:1 so adoption is a
    drop-in replacement with no visual change:
      - 'icon' → small buttons with leading icons (OtherAssetsView)
      - 'link' → link-style text buttons (MenuSettingView)
    The default slot renders after the pair for any extra row actions.
  -->
  <template v-if="variant === 'link'">
    <el-button link type="primary" @click="emit('edit')">{{ editLabel }}</el-button>
    <el-button link type="danger" @click="emit('delete')">{{ deleteLabel }}</el-button>
  </template>
  <template v-else>
    <el-button size="small" :icon="Edit" @click="emit('edit')">{{ editLabel }}</el-button>
    <el-button size="small" type="danger" :icon="Delete" @click="emit('delete')">
      {{ deleteLabel }}
    </el-button>
  </template>
  <slot />
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { Edit, Delete } from '@element-plus/icons-vue'

const props = withDefaults(
  defineProps<{
    variant?: 'icon' | 'link'
    editText?: string
    deleteText?: string
  }>(),
  {
    variant: 'icon',
  },
)

const emit = defineEmits<{
  (e: 'edit'): void
  (e: 'delete'): void
}>()

const { t } = useI18n()

// Default to the shared common.* labels; callers can still override per-row.
const editLabel = computed(() => props.editText ?? t('common.edit'))
const deleteLabel = computed(() => props.deleteText ?? t('common.delete'))
</script>
