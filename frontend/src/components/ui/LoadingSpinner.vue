<!-- components/ui/LoadingSpinner.vue -->
<template>
  <div
    :class="[
      'flex items-center justify-center',
      fullScreen ? 'fixed inset-0 bg-gray-100/50 z-50' : 'w-full py-12'
    ]"
  >
    <div class="flex flex-col items-center">
      <svg
        class="animate-spin h-8 w-8 text-primary-600"
        xmlns="http://www.w3.org/2000/svg"
        fill="none"
        viewBox="0 0 24 24"
      >
        <circle
          class="opacity-25"
          cx="12"
          cy="12"
          r="10"
          stroke="currentColor"
          stroke-width="4"
        />
        <path
          class="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
        />
      </svg>
      <span v-if="text" class="mt-2 text-sm text-gray-500">{{ text }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  fullScreen?: boolean
  text?: string
}>()
</script>