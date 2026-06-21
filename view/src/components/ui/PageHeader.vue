<template>
  <div class="flex flex-wrap items-end justify-between gap-4">
    <div class="flex flex-col gap-1">
      <h1 class="text-on-surface text-3xl lg:text-4xl font-extrabold leading-tight tracking-tight">
        {{ title }}
      </h1>
      <p v-if="subtitle" class="text-on-surface-variant text-base">
        {{ subtitle }}
      </p>
    </div>
    <div v-if="$slots.actions" class="flex gap-3">
      <slot name="actions" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; subtitle?: string }>()
</script>
