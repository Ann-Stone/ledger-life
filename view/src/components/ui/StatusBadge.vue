<template>
  <!-- Custom design-system variants -->
  <span
    v-if="resolvedVariant === 'primary'"
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-label-caps bg-primary-container/10 text-primary-container"
  >
    <slot>{{ value }}</slot>
  </span>
  <span
    v-else-if="resolvedVariant === 'secondary'"
    class="inline-flex items-center px-2.5 py-0.5 rounded-full text-label-caps bg-secondary/10 text-secondary"
  >
    <slot>{{ value }}</slot>
  </span>
  <!-- Element Plus variants -->
  <el-tag v-else :type="resolvedVariant" size="small" round>
    <slot>{{ value }}</slot>
  </el-tag>
</template>

<script setup lang="ts">
import { computed } from 'vue'

type EpTagType = 'success' | 'danger' | 'info' | 'warning'
type BadgeVariant = 'primary' | 'secondary' | EpTagType

const props = withDefaults(
  defineProps<{
    value?: string
    type?: EpTagType
    variant?: BadgeVariant
  }>(),
  { variant: undefined },
)

const resolvedVariant = computed<BadgeVariant>(() => {
  if (props.variant) return props.variant
  if (props.type) return props.type
  // Legacy auto-resolve from value string
  if (props.value === 'Y') return 'success'
  if (props.value === 'N') return 'danger'
  return 'info'
})
</script>
