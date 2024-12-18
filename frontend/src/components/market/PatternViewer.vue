<!-- components/market/PatternViewer.vue -->
<template>
  <div class="bg-white p-4 rounded-lg shadow">
    <h3 class="text-lg font-medium mb-4">Обнаруженные паттерны</h3>

    <div class="space-y-4">
      <template v-if="patterns.length">
        <div
          v-for="pattern in patterns"
          :key="`${pattern.pattern}-${pattern.start}`"
          class="border rounded-lg p-3"
        >
          <div class="flex justify-between items-start">
            <div>
              <h4 class="font-medium">{{ pattern.pattern }}</h4>
              <p class="text-sm text-gray-500">
                Надежность: {{ formatPercent(pattern.reliability * 100) }}
              </p>
            </div>
            <div
              class="px-2 py-1 rounded text-sm"
              :class="pattern.signal === 'buy' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'"
            >
              {{ pattern.signal === 'buy' ? 'Покупка' : 'Продажа' }}
            </div>
          </div>
        </div>
      </template>
      <div v-else class="text-gray-500 text-center py-4">
        Паттерны не обнаружены
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { PatternMatch } from '@/utils/patternAnalysis'
import { formatPercent } from '@/utils/formatters'

defineProps<{
  patterns: PatternMatch[]
}>()
</script>