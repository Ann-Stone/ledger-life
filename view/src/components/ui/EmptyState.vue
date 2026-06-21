<template>
  <el-empty :description="message ?? t('common.empty')" class="custom-empty">
    <template #image>
      <svg
        class="w-24 h-24 mx-auto"
        viewBox="0 0 120 120"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
      >
        <!-- Background dashed circle -->
        <circle
          cx="60"
          cy="60"
          r="48"
          stroke="var(--ds-outline-variant)"
          stroke-opacity="0.4"
          stroke-width="1.5"
          stroke-dasharray="4 4"
          fill="var(--ds-surface-container-lowest)"
          fill-opacity="0.15"
        />
        
        <!-- Minimalist document folder / box body -->
        <path
          d="M36 48H84V78C84 81.3137 81.3137 84 78 84H42C38.6863 84 36 81.3137 36 78V48Z"
          fill="var(--ds-surface-container-highest)"
          fill-opacity="0.3"
          stroke="var(--ds-outline)"
          stroke-width="1.5"
          stroke-linejoin="round"
        />
        
        <!-- Box cover lid with brand primary accent -->
        <path
          d="M32 40H88V48H32V40Z"
          fill="var(--ds-primary)"
          fill-opacity="0.2"
          stroke="var(--ds-primary)"
          stroke-width="1.5"
          stroke-linejoin="round"
        />
        
        <!-- Minimalist center handle line -->
        <path
          d="M52 64H68"
          stroke="var(--ds-outline)"
          stroke-width="2"
          stroke-linecap="round"
        />
      </svg>
    </template>
  </el-empty>
</template>

<script setup lang="ts">
const { t } = useI18n()
defineProps<{ message?: string }>()
</script>

<style scoped>
.custom-empty {
  padding: 16px 0;
}
:deep(.el-empty__image) {
  width: auto !important;
  height: auto !important;
}
:deep(.el-empty__description) {
  margin-top: 8px !important;
}
:deep(.el-empty__description p) {
  color: var(--ds-on-surface-variant) !important;
  font-size: calc(13px * var(--app-font-scale)) !important;
  font-weight: 500 !important;
}
</style>
