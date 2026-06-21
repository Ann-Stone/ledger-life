<template>
  <button
    type="button"
    class="w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm bg-transparent border-0 outline-none cursor-pointer text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface transition-colors"
    :class="{ 'justify-center': collapsed }"
    @click="emit('toggle')"
  >
    <el-icon class="shrink-0 text-base">
      <component :is="icon" />
    </el-icon>
    <span v-if="!collapsed" class="flex-1 text-left font-medium">{{ label }}</span>
    <el-icon
      v-if="!collapsed"
      class="text-xs transition-transform"
      :class="expanded ? 'rotate-90' : ''"
    >
      <ArrowRight />
    </el-icon>
  </button>
</template>

<script setup lang="ts">
import type { Component } from 'vue'
import { ArrowRight } from '@element-plus/icons-vue'

defineProps<{
  label: string
  icon: Component
  expanded: boolean
  collapsed: boolean
}>()

const emit = defineEmits<{ (e: 'toggle'): void }>()
</script>
