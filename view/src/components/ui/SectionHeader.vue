<template>
  <div class="flex items-center justify-between border-b border-outline-variant pb-3">
    <h2 class="text-on-surface text-xl font-bold leading-tight tracking-tight">
      {{ title }}
    </h2>
    <slot name="actions">
      <button
        v-if="actionText"
        type="button"
        class="text-primary text-sm font-bold hover:underline"
        @click="emit('action')"
      >
        {{ actionText }}
      </button>
    </slot>
  </div>
</template>

<script setup lang="ts">
defineProps<{ title: string; actionText?: string }>()
const emit = defineEmits<{ (e: 'action'): void }>()
</script>
