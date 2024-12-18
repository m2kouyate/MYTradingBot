<!-- components/strategy/StrategyFormModal.vue -->
<template>
  <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" />
  <div class="fixed inset-0 z-10 overflow-y-auto">
    <div class="flex min-h-full items-end justify-center p-4 text-center sm:items-center sm:p-0">
      <div class="relative transform overflow-hidden rounded-lg bg-white px-4 pb-4 pt-5 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg sm:p-6">
        <div>
          <h3 class="text-xl font-semibold leading-6 text-gray-900">
            {{ props.strategy ? 'Редактирование стратегии' : 'Создание стратегии' }}
          </h3>
          <form @submit.prevent="handleSubmit" class="mt-5 space-y-4">
            <div>
              <label for="name" class="block text-sm font-medium text-gray-700">Название</label>
              <input
                type="text"
                id="name"
                v-model="form.name"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                required
              />
            </div>

            <div>
              <label for="symbol" class="block text-sm font-medium text-gray-700">Торговая пара</label>
              <input
                type="text"
                id="symbol"
                v-model="form.symbol"
                class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                required
              />
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="takeProfit" class="block text-sm font-medium text-gray-700">Take Profit (%)</label>
                <input
                  type="number"
                  id="takeProfit"
                  v-model="form.takeProfit"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label for="stopLoss" class="block text-sm font-medium text-gray-700">Stop Loss (%)</label>
                <input
                  type="number"
                  id="stopLoss"
                  v-model="form.stopLoss"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>
            </div>

            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="buyThreshold" class="block text-sm font-medium text-gray-700">Buy Threshold</label>
                <input
                  type="number"
                  id="buyThreshold"
                  v-model="form.buyThreshold"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>

              <div>
                <label for="sellThreshold" class="block text-sm font-medium text-gray-700">Sell Threshold</label>
                <input
                  type="number"
                  id="sellThreshold"
                  v-model="form.sellThreshold"
                  step="0.1"
                  class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500"
                  required
                />
              </div>
            </div>

            <div class="mt-5 sm:mt-6 sm:grid sm:grid-flow-row-dense sm:grid-cols-2 sm:gap-3">
              <button
                type="submit"
                class="inline-flex w-full justify-center rounded-md bg-primary-600 px-3 py-2 text-sm font-semibold text-white shadow-sm hover:bg-primary-500 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary-600 sm:col-start-2"
              >
                {{ props.strategy ? 'Сохранить' : 'Создать' }}
              </button>
              <button
                type="button"
                @click="emit('close')"
                class="mt-3 inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 hover:bg-gray-50 sm:col-start-1 sm:mt-0"
              >
                Отмена
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import type { Strategy } from '@/types/trading'

const props = defineProps<{
  strategy?: Strategy | null
}>()

const emit = defineEmits<{
  close: []
  save: [strategy: Strategy]
}>()

const defaultForm = {
  name: '',
  symbol: '',
  takeProfit: 0,
  stopLoss: 0,
  buyThreshold: 0,
  sellThreshold: 0,
  isActive: false
}

const form = ref({ ...defaultForm })

onMounted(() => {
  if (props.strategy) {
    form.value = { ...props.strategy }
  }
})

function handleSubmit() {
  emit('save', {
    ...form.value,
    id: props.strategy?.id
  } as Strategy)
}
</script>