<!-- components/ui/ErrorState.vue -->
<template>
  <div class="flex flex-col items-center justify-center py-12">
    <div class="rounded-full bg-red-100 p-3">
      <ExclamationCircleIcon class="h-6 w-6 text-red-600" />
    </div>
    <h3 class="mt-2 text-sm font-medium text-gray-900">{{ title }}</h3>
    <p class="mt-1 text-sm text-gray-500">{{ message }}</p>
    <div class="mt-6">
      <button
        @click="$emit('retry')"
        type="button"
        class="inline-flex items-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-700"
      >
        <ArrowPathIcon class="-ml-0.5 mr-1.5 h-5 w-5" aria-hidden="true" />
        Попробовать снова
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ExclamationCircleIcon, ArrowPathIcon } from '@heroicons/vue/24/outline'

defineProps<{
  title?: string
  message: string
}>()

defineEmits<{
  retry: []
}>()
</script>