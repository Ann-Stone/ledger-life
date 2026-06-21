<template>
  <div class="flex flex-col items-center justify-center h-full gap-4 text-on-surface-variant">
    <p class="text-6xl font-bold text-outline-variant">404</p>
    <p class="text-xl">{{ t('notFound.title') }}</p>
    <el-button type="primary" @click="router.push('/dashboard')">{{ t('notFound.back') }}</el-button>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router'
const router = useRouter()
const { t } = useI18n()
</script>
