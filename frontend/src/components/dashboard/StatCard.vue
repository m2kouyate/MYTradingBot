<!-- components/dashboard/StatCard.vue -->
<template>
  <div class="bg-white px-4 py-5 shadow rounded-lg sm:p-6">
    <template v-if="isLoading">
      <SkeletonLoader :width="120" :height="20" />
      <SkeletonLoader class="mt-2" :width="80" :height="36" />
      <SkeletonLoader v-if="showChange" class="mt-2" :width="100" :height="20" />
    </template>
    <template v-else>
      <dt class="text-sm font-medium text-gray-500 truncate">{{ title }}</dt>
      <dd class="mt-1 text-3xl font-semibold" :class="valueClass">{{ value }}</dd>
      <p v-if="change" class="mt-2 text-sm flex items-center gap-1" :class="changeClass">
        <ArrowUp v-if="change.value >= 0" class="h-4 w-4" />
        <ArrowDown v-else class="h-4 w-4" />
        {{ formatPercent(Math.abs(change.value)) }}
        {{ change.text }}
      </p>
    </template>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { ArrowUp, ArrowDown } from 'lucide-vue-next'
import { formatPercent } from '@/utils/formatters'
import SkeletonLoader from '@/components/ui/SkeletonLoader.vue'

interface Change {
  value: number
  text: string
}

const props = defineProps<{
  isLoading?: boolean
  title: string
  value: string | number
  valueClass?: string
  change?: Change
  showChange?: boolean
}>()

const changeClass = computed(() =>
  props.change?.value >= 0 ? 'text-green-600' : 'text-red-600'
)
</script>