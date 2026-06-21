<template>
  <!-- Desktop sidebar -->
  <aside
    v-if="!appStore.isMobile"
    class="fixed left-0 top-0 h-full z-20 bg-surface-container-low text-on-surface border-r border-outline-variant transition-all duration-300 flex flex-col"
    :class="appStore.sidebarCollapsed ? 'w-16' : 'w-[220px]'"
  >
    <SidebarContent :collapsed="appStore.sidebarCollapsed" />
  </aside>

  <!-- Mobile drawer -->
  <aside
    v-else
    class="fixed left-0 top-0 h-full z-40 w-[220px] bg-surface-container-low text-on-surface border-r border-outline-variant transition-transform duration-300 flex flex-col"
    :class="appStore.sidebarDrawerVisible ? 'translate-x-0' : '-translate-x-full'"
  >
    <SidebarContent :collapsed="false" />
  </aside>
</template>

<script setup lang="ts">
import { useAppStore } from '@/stores/app'
import SidebarContent from './SidebarContent.vue'

const appStore = useAppStore()
</script>
