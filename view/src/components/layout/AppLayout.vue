<template>
  <div class="flex h-screen bg-surface overflow-hidden">
    <!-- Sidebar -->
    <Sidebar />

    <!-- Mobile overlay -->
    <div
      v-if="appStore.isMobile && appStore.sidebarDrawerVisible"
      class="fixed inset-0 z-30 bg-black/40"
      @click="appStore.closeSidebarDrawer()"
    />

    <!-- Main content area -->
    <div
      class="flex flex-col flex-1 min-w-0 transition-all duration-300"
      :class="appStore.isMobile ? 'ml-0' : (appStore.sidebarCollapsed ? 'ml-16' : 'ml-[220px]')"
    >
      <!-- Navbar -->
      <Navbar />

      <!-- Page content -->
      <main class="flex-1 overflow-y-auto p-6 flex flex-col">
        <router-view v-slot="{ Component }">
          <keep-alive :include="keepAliveViews">
            <component :is="Component" />
          </keep-alive>
        </router-view>
      </main>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted } from 'vue'
import { useAppStore } from '@/stores/app'
import Sidebar from './Sidebar.vue'
import Navbar from './Navbar.vue'

const appStore = useAppStore()

// Views to cache with keep-alive
const keepAliveViews = ['DashboardView', 'OtherAssetsView']

const checkMobile = () => {
  appStore.setMobile(window.innerWidth < 768)
}

onMounted(() => {
  checkMobile()
  window.addEventListener('resize', checkMobile)
})

onUnmounted(() => {
  window.removeEventListener('resize', checkMobile)
})
</script>
