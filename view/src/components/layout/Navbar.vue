<template>
  <header class="h-14 bg-surface-container border-b border-outline-variant flex items-center px-4 gap-4 shrink-0">
    <!-- Hamburger / toggle -->
    <button
      class="p-1.5 rounded-lg bg-transparent border-0 outline-none cursor-pointer text-on-surface-variant hover:bg-surface-container-high transition-colors"
      @click="appStore.toggleSidebar()"
    >
      <el-icon class="text-xl"><Expand v-if="appStore.sidebarCollapsed" /><Fold v-else /></el-icon>
    </button>

    <!-- Breadcrumb -->
    <el-breadcrumb separator="/">
      <el-breadcrumb-item :to="{ path: '/dashboard' }">{{ t('route.home') }}</el-breadcrumb-item>
      <el-breadcrumb-item
        v-for="crumb in breadcrumbs"
        :key="crumb"
      >
        {{ crumb }}
      </el-breadcrumb-item>
    </el-breadcrumb>

    <!-- Spacer -->
    <div class="flex-1" />

    <!-- Urgent alarm pill -->
    <AlarmPill />

    <!-- Spacer between pill and right cluster -->
    <div class="w-2" />

    <!-- Language toggle -->
    <el-button-group size="small">
      <el-button
        :type="appStore.locale === 'zh-TW' ? 'primary' : 'default'"
        @click="appStore.setLocale('zh-TW')"
      >
        中文
      </el-button>
      <el-button
        :type="appStore.locale === 'en' ? 'primary' : 'default'"
        @click="appStore.setLocale('en')"
      >
        EN
      </el-button>
    </el-button-group>

    <!-- Font size selector -->
    <el-dropdown trigger="click" @command="appStore.setFontScale($event)">
      <el-button size="small" :title="t('nav.adjustFontSize')">
        <span class="font-semibold leading-none">A<span class="text-[0.7em] align-baseline">A</span></span>
      </el-button>
      <template #dropdown>
        <el-dropdown-menu>
          <el-dropdown-item
            v-for="opt in fontScaleOptions"
            :key="opt.value"
            :command="opt.value"
            :class="{ 'is-active-scale': appStore.fontScale === opt.value }"
          >
            <span :class="{ 'font-semibold': appStore.fontScale === opt.value }">
              {{ t(opt.labelKey) }}
            </span>
          </el-dropdown-item>
        </el-dropdown-menu>
      </template>
    </el-dropdown>

    <!-- Theme toggle -->
    <el-button
      size="small"
      :title="appStore.theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'"
      @click="appStore.toggleTheme()"
    >
      <el-icon><Sunny v-if="appStore.theme === 'dark'" /><Moon v-else /></el-icon>
    </el-button>
  </header>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore, type FontScale } from '@/stores/app'
import { useAlarmStore } from '@/stores/alarms'
import { Expand, Fold, Sunny, Moon } from '@element-plus/icons-vue'
import AlarmPill from './AlarmPill.vue'

const fontScaleOptions: { value: FontScale; labelKey: string }[] = [
  { value: 'xs', labelKey: 'nav.fontXS' },
  { value: 'sm', labelKey: 'nav.fontSM' },
  { value: 'md', labelKey: 'nav.fontMD' },
  { value: 'lg', labelKey: 'nav.fontLG' },
  { value: 'xl', labelKey: 'nav.fontXL' },
]

const appStore = useAppStore()
const alarmStore = useAlarmStore()
const route = useRoute()
const { t } = useI18n()

if (alarmStore.alarms.length === 0) {
  alarmStore.fetchAlarms()
}

const breadcrumbs = computed<string[]>(() => {
  const meta = route.meta as { breadcrumbKeys?: string[] }
  return (meta.breadcrumbKeys ?? []).map((k) => t(k))
})
</script>
