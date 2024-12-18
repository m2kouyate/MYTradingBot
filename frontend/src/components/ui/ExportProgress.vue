<!-- components/ui/ExportProgress.vue -->
<template>
  <TransitionRoot
    appear
    show
    as="template"
  >
    <div class="fixed inset-0 z-50 flex items-center justify-center">
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75" />

      <TransitionChild
        appear
        enter="ease-out duration-300"
        enter-from="opacity-0 scale-95"
        enter-to="opacity-100 scale-100"
        leave="ease-in duration-200"
        leave-from="opacity-100 scale-100"
        leave-to="opacity-0 scale-95"
      >
        <div class="relative bg-white rounded-lg p-6 max-w-sm w-full shadow-xl">
          <div class="text-center">
            <h3 class="text-lg font-medium text-gray-900">Экспорт данных</h3>
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
            </div>
          </div>
        </div>
      </TransitionChild>
    </div>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { TransitionRoot, TransitionChild } from '@headlessui/vue'

defineProps<{
  progress: number
}>()
</script>