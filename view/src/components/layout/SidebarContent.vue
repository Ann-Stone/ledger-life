<template>
  <div class="flex flex-col h-full">
    <!-- Logo -->
    <div class="flex items-center h-14 px-4 border-b border-outline-variant shrink-0">
      <span v-if="!collapsed" class="font-bold text-base tracking-wide truncate text-on-surface">
        Balance Sheet
      </span>
      <span v-else class="font-bold text-base text-on-surface">BS</span>
    </div>

    <!-- Navigation -->
    <nav class="flex-1 overflow-y-auto py-3 space-y-1 px-2">
      <template v-for="item in menuItems" :key="item.name">
        <!-- Group label -->
        <div
          v-if="!collapsed && item.type === 'group'"
          class="px-2 pt-3 pb-1 text-[10px] font-bold uppercase tracking-widest text-on-surface-variant"
        >
          {{ t(item.labelKey) }}
        </div>

        <!-- Nav item with children -->
        <template v-if="item.children">
          <SidebarNavButton
            :label="t(item.labelKey)"
            :icon="item.icon"
            :expanded="openGroups.has(item.name)"
            :collapsed="collapsed"
            @toggle="toggleGroup(item.name)"
          />
          <div v-show="!collapsed && openGroups.has(item.name)" class="ml-4 space-y-1">
            <router-link
              v-for="child in item.children"
              :key="child.name"
              :to="child.path"
              class="flex items-center gap-2 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
              :class="
                isActive(child.path)
                  ? 'bg-primary/15 text-primary'
                  : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface'
              "
              @click="onNavClick"
            >
              <span class="w-1.5 h-1.5 rounded-full bg-current shrink-0" />
              {{ t(child.labelKey) }}
            </router-link>
          </div>
        </template>

        <!-- Single nav item -->
        <router-link
          v-else-if="item.type === 'link'"
          :to="item.path!"
          class="flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-colors"
          :class="[
            { 'justify-center': collapsed },
            isActive(item.path!)
              ? 'bg-primary/15 text-primary'
              : 'text-on-surface-variant hover:bg-surface-container-high hover:text-on-surface',
          ]"
          @click="onNavClick"
        >
          <el-icon class="shrink-0 text-base">
            <component :is="item.icon" />
          </el-icon>
          <span v-if="!collapsed" class="truncate">{{ t(item.labelKey) }}</span>
        </router-link>
      </template>
    </nav>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRoute } from 'vue-router'
import { useAppStore } from '@/stores/app'
import SidebarNavButton from './SidebarNavButton.vue'
import {
  Odometer,
  Notebook,
  Document,
  Coin,
  Setting,
  Tools,
} from '@element-plus/icons-vue'

defineProps<{ collapsed: boolean }>()

const route = useRoute()
const appStore = useAppStore()
const { t } = useI18n()
const openGroups = ref<Set<string>>(new Set(['reports', 'setting', 'utilities']))

const menuItems = [
  {
    type: 'link',
    name: 'dashboard',
    labelKey: 'nav.dashboard',
    path: '/dashboard',
    icon: Odometer,
  },
  {
    type: 'link',
    name: 'cashFlow',
    labelKey: 'nav.cashFlow',
    path: '/monthly-report/cash-flow',
    icon: Notebook,
  },
  {
    type: 'link',
    name: 'otherAssets',
    labelKey: 'nav.otherAssets',
    path: '/other-assets',
    icon: Coin,
  },
  {
    type: 'group',
    name: 'reports',
    labelKey: 'nav.reports',
    icon: Document,
    children: [
      { name: 'balanceSheet', labelKey: 'nav.balanceSheet', path: '/year-report/balance-sheet' },
      { name: 'incomeStatement', labelKey: 'nav.incomeStatement', path: '/year-report/income-statement' },
      { name: 'cashFlowStatement', labelKey: 'nav.cashFlowStatement', path: '/year-report/cash-flow-statement' },
      { name: 'spending', labelKey: 'nav.spending', path: '/year-report/spending' },
      { name: 'assets', labelKey: 'nav.assets', path: '/year-report/assets' },
    ],
  },
  {
    type: 'group',
    name: 'setting',
    labelKey: 'nav.settings',
    icon: Setting,
    children: [
      { name: 'settingMenu', labelKey: 'nav.settingMenu', path: '/setting/menu' },
      { name: 'settingBudget', labelKey: 'nav.settingBudget', path: '/setting/budget' },
      { name: 'settingRemind', labelKey: 'nav.settingRemind', path: '/setting/remind' },
    ],
  },
  {
    type: 'group',
    name: 'utilities',
    labelKey: 'nav.utilities',
    icon: Tools,
    children: [
      { name: 'utilitiesImport', labelKey: 'nav.import', path: '/utilities/import' },
      {
        name: 'retirementReadiness',
        labelKey: 'nav.retirementReadiness',
        path: '/utilities/retirement-readiness',
      },
    ],
  },
]

const toggleGroup = (name: string) => {
  if (openGroups.value.has(name)) {
    openGroups.value.delete(name)
  } else {
    openGroups.value.add(name)
  }
}

const isActive = (path: string) => route.path === path || route.path.startsWith(path + '/')

const onNavClick = () => {
  if (appStore.isMobile) {
    appStore.closeSidebarDrawer()
  }
}
</script>
