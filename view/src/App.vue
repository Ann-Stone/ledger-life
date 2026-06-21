<template>
  <el-config-provider :locale="elementLocale">
    <router-view />
  </el-config-provider>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import zhTw from 'element-plus/es/locale/lang/zh-tw'
import en from 'element-plus/es/locale/lang/en'
import { useAppStore } from '@/stores/app'

const appStore = useAppStore()
const elementLocale = computed(() => (appStore.locale === 'en' ? en : zhTw))
</script>
