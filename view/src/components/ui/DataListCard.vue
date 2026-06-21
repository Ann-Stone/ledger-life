<template>
  <div class="bg-surface-container rounded-xl border border-outline-variant overflow-hidden flex flex-col">
    <div
      v-if="title || $slots.menu"
      class="px-6 py-4 border-b border-outline-variant/30 bg-surface-container-low flex justify-between items-center shrink-0"
    >
      <p class="text-sm font-bold text-on-surface">{{ title }}</p>
      <slot name="menu" />
    </div>
    <div class="divide-y divide-outline-variant/20 flex-1 min-h-0 overflow-y-auto">
      <slot />
    </div>
    <div
      v-if="$slots.footer"
      class="p-4 bg-surface-container-low text-center shrink-0"
    >
      <slot name="footer" />
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title?: string }>()
</script>
