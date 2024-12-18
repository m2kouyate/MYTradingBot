<!-- components/ui/SkeletonLoader.vue -->
<template>
  <div
    :class="[
      'animate-pulse bg-gray-200 rounded',
      { 'w-full': width === 'full' }
    ]"
    :style="{
      width: typeof width === 'number' ? `${width}px` : undefined,
      height: `${height}px`
    }"
  >
    <span class="sr-only">Loading...</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  width?: number | 'full'
  height: number
}>()
</script>