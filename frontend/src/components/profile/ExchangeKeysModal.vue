<template>
  <TransitionRoot appear show as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <div class="fixed inset-0 bg-black/30" />

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-lg bg-white p-6 shadow-xl transition-all">
            <div class="flex justify-between items-start">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                {{ exchangeKey ? 'Редактирование API ключей' : 'Добавление API ключей' }}
              </DialogTitle>
              <button
                @click="closeModal"
                class="rounded-md text-gray-400 hover:text-gray-500"
              >
                <X class="h-6 w-6" />
              </button>
            </div>

            <form @submit.prevent="handleSubmit" class="mt-4">
              <div class="space-y-4">
                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    Биржа
                  </label>
                  <select
                    v-model="form.exchange"
                    required
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  >
                    <option value="">Выберите биржу</option>
                    <option value="BINANCE">Binance</option>
                    <option value="BYBIT">Bybit</option>
                  </select>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    API Key
                  </label>
                  <input
                    type="text"
                    v-model="form.api_key"
                    required
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    API Secret
                  </label>
                  <input
                    type="password"
                    v-model="form.api_secret"
                    required
                    class="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 sm:text-sm"
                  />
                </div>

                <div>
                  <div class="flex items-center">
                    <input
                      type="checkbox"
                      v-model="form.testnet"
                      class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
                    />
                    <label class="ml-2 block text-sm text-gray-700">
                      Тестовая сеть (Testnet)
                    </label>
                  </div>
                  <p class="mt-1 text-sm text-gray-500">
                    Включите для использования тестового API биржи
                  </p>
                </div>
              </div>

              <div class="mt-6 flex justify-end space-x-3">
                <button
                  type="button"
                  @click="closeModal"
                  class="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md shadow-sm hover:bg-gray-50"
                >
                  Отмена
                </button>
                <button
                  type="submit"
                  :disabled="isLoading"
                  class="inline-flex justify-center px-4 py-2 text-sm font-medium text-white bg-primary-600 border border-transparent rounded-md shadow-sm hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                  <Loader v-if="isLoading" class="animate-spin -ml-1 mr-2 h-5 w-5" />
                  {{ isLoading ? 'Сохранение...' : 'Сохранить' }}
                </button>
              </div>
            </form>
          </DialogPanel>
        </div>
      </div>
    </Dialog>
  </TransitionRoot>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Dialog, DialogPanel, DialogTitle, TransitionRoot } from '@headlessui/vue'
import { X, Loader } from 'lucide-vue-next'
import { apiClient } from '@/services/api'
import { API_ENDPOINTS } from '@/constants/api'
import { useNotificationStore } from '@/stores/notification'

interface ExchangeKey {
  id: number
  exchange: string
  api_key: string
  api_secret: string
  testnet: boolean
}

const props = defineProps<{
  exchangeKey?: ExchangeKey | null
}>()

const emit = defineEmits<{
  close: []
  save: []
}>()

const notificationStore = useNotificationStore()
const isLoading = ref(false)

const form = ref({
  exchange: props.exchangeKey?.exchange || '',
  api_key: props.exchangeKey?.api_key || '',
  api_secret: props.exchangeKey?.api_secret || '',
  testnet: props.exchangeKey?.testnet || false
})

async function handleSubmit() {
  isLoading.value = true
  try {
    if (props.exchangeKey) {
      await apiClient.put(
        API_ENDPOINTS.EXCHANGE_KEYS.UPDATE(props.exchangeKey.id),
        form.value
      )
    } else {
      await apiClient.post(API_ENDPOINTS.EXCHANGE_KEYS.CREATE, form.value)
    }

    notificationStore.showSuccess('API ключи успешно сохранены')
    emit('save')
    closeModal()
  } catch (error) {
    notificationStore.showError('Ошибка при сохранении API ключей')
  } finally {
    isLoading.value = false
  }
}

function closeModal() {
  emit('close')
}
</script>