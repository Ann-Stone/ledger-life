<!--
  Share-of-total percent cell for report tables: one decimal + '%', or an
  em-dash when the share is unavailable. Color/size classes come from the
  caller via attribute fallthrough.
-->
<template>
  <span v-if="value != null" class="tabular-nums">{{ value.toFixed(1) }}%</span>
  <span v-else class="text-on-surface-variant/40">—</span>
</template>

<script setup lang="ts">
defineOptions({ name: 'SharePercent' })

defineProps<{
  value?: number | null
}>()
</script>
