<!-- components/strategy/BacktestProgress.vue -->
<template>
  <div class="fixed inset-0 z-50 flex items-center justify-center">
    <div class="fixed inset-0 bg-gray-500 bg-opacity-75" />

    <div class="relative bg-white rounded-lg p-6 max-w-sm w-full shadow-xl">
      <div class="text-center">
        <div class="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-primary-100">
          <ChartBarIcon class="h-6 w-6 text-primary-600 animate-pulse" />
        </div>

        <h3 class="mt-4 text-lg font-medium text-gray-900">
          Выполняется бэктест
        </h3>

        <div class="mt-4">
          <div class="relative pt-1">
            <div class="overflow-hidden h-2 mb-4 text-xs flex rounded bg-primary-100">
              <div
                :style="{ width: `${progress}%` }"
                class="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-primary-500 transition-all duration-300"
              />
            </div>
          </div>
          <p class="text-sm text-gray-500">{{ progress.toFixed(0) }}% завершено</p>
          <p class="mt-2 text-sm text-gray-600">{{ status }}</p>
        </div>

        <div v-if="canCancel" class="mt-6">
          <button
            type="button"
            @click="$emit('cancel')"
            class="inline-flex justify-center rounded-md border border-gray-300 bg-white px-4 py-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
          >
            Отменить
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ChartBarIcon } from '@heroicons/vue/24/outline'

defineProps<{
  progress: number
  status: string
  canCancel?: boolean
}>()

defineEmits<{
  cancel: []
}>()
</script>