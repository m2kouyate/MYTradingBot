<template>
  <div>
    <div class="flex justify-between items-center mb-6">
      <h1 class="text-2xl font-semibold text-gray-900">Профиль пользователя</h1>
      <button
        @click="editMode = !editMode"
        class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50"
      >
        <Pencil v-if="!editMode" class="-ml-1 mr-2 h-5 w-5 text-gray-500" />
        <X v-else class="-ml-1 mr-2 h-5 w-5 text-gray-500" />
        {{ editMode ? 'Отменить' : 'Редактировать' }}
      </button>
    </div>

    <div class="bg-white shadow rounded-lg">
      <div class="px-4 py-5 sm:p-6">
        <!-- Основная информация -->
        <div class="space-y-6">
          <div>
            <h3 class="text-lg font-medium leading-6 text-gray-900">Основная информация</h3>
            <div class="mt-4 grid grid-cols-1 gap-y-6 sm:grid-cols-2 sm:gap-x-4">
              <div>
                <label class="block text-sm font-medium text-gray-700">Email</label>
                <div class="mt-1">
                  <p v-if="!editMode" class="text-sm text-gray-900">{{ user?.email }}</p>
                  <input
                    v-else
                    type="email"
                    v-model="profileForm.email"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">Имя пользователя</label>
                <div class="mt-1">
                  <p v-if="!editMode" class="text-sm text-gray-900">{{ user?.username }}</p>
                  <input
                    v-else
                    type="text"
                    v-model="profileForm.username"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                    disabled
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">Имя</label>
                <div class="mt-1">
                  <p v-if="!editMode" class="text-sm text-gray-900">{{ user?.first_name || '—' }}</p>
                  <input
                    v-else
                    type="text"
                    v-model="profileForm.first_name"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                </div>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700">Фамилия</label>
                <div class="mt-1">
                  <p v-if="!editMode" class="text-sm text-gray-900">{{ user?.last_name || '—' }}</p>
                  <input
                    v-else
                    type="text"
                    v-model="profileForm.last_name"
                    class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                </div>
              </div>
            </div>
          </div>

          <!-- Кнопки сохранения -->
          <div v-if="editMode" class="flex justify-end">
            <button
              type="button"
              @click="saveProfile"
              :disabled="isLoading"
              class="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
            >
              <Loader v-if="isLoading" class="animate-spin -ml-1 mr-2 h-5 w-5" />
              {{ isLoading ? 'Сохранение...' : 'Сохранить изменения' }}
            </button>
          </div>
        </div>

        <!-- Безопасность -->
        <div class="mt-10 pt-6 border-t border-gray-200">
          <h3 class="text-lg font-medium leading-6 text-gray-900">Безопасность</h3>
          <div class="mt-4">
            <button
              type="button"
              @click="showPasswordModal = true"
              class="inline-flex items-center px-4 py-2 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
            >
              <Key class="-ml-1 mr-2 h-5 w-5 text-gray-500" />
              Сменить пароль
            </button>
          </div>
        </div>

        <!-- API ключи бирж -->
        <div class="mt-10 pt-6 border-t border-gray-200">
      <div class="flex justify-between items-center">
        <h3 class="text-lg font-medium leading-6 text-gray-900">API ключи бирж</h3>
        <button
          type="button"
          @click="openExchangeModal()"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50"
        >
          <Plus class="-ml-0.5 mr-2 h-4 w-4" />
          Добавить ключи
        </button>
      </div>
      <div class="mt-4 space-y-4">
        <div v-for="key in exchangeKeys" :key="key.id" class="flex items-center justify-between bg-white p-4 rounded-lg border">
          <div>
            <h4 class="text-sm font-medium text-gray-900">{{ key.exchange }}</h4>
            <p class="text-sm text-gray-500">API Key: {{ maskApiKey(key.api_key) }}</p>
          </div>
          <div class="flex items-center space-x-2">
            <button
              @click="verifyKey(key)"
              class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
            >
              Проверить
            </button>
            <button
              @click="openExchangeModal(key)"
              class="inline-flex items-center px-2.5 py-1.5 border border-gray-300 shadow-sm text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50"
            >
              Изменить
            </button>
            <button
              @click="deleteKey(key)"
              class="inline-flex items-center px-2.5 py-1.5 border border-red-300 shadow-sm text-xs font-medium rounded text-red-700 bg-white hover:bg-red-50"
            >
              Удалить
            </button>
          </div>
        </div>
      </div>
    </div>

        <!-- Модальные окна -->
        <ChangePasswordModal
          v-if="showPasswordModal"
          @close="showPasswordModal = false"
        />

        <ExchangeKeysModal
          v-if="isExchangeModalOpen"
          :exchange-key="selectedExchangeKey"
          @close="closeExchangeModal"
          @save="handleExchangeKeySave"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { Pencil, X, Loader, Key, Plus } from 'lucide-vue-next'
import ChangePasswordModal from '@/components/profile/ChangePasswordModal.vue'
import ExchangeKeysModal from '@/components/profile/ExchangeKeysModal.vue'
import type { User } from '@/types/api'
import { apiClient } from '@/services/api'
import { API_ENDPOINTS } from '@/constants/api'
import { useNotificationStore } from '@/stores/notification'

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const editMode = ref(false)
const isLoading = ref(false)
const showPasswordModal = ref(false)
const isExchangeModalOpen = ref(false)
const selectedExchangeKey = ref<any | null>(null)
const exchangeKeys = ref([])

const user = computed(() => authStore.user)

const profileForm = ref({
  email: user.value?.email || '',
  username: user.value?.username || '',
  first_name: user.value?.first_name || '',
  last_name: user.value?.last_name || ''
})

// Функции
async function saveProfile() {
  isLoading.value = true
  try {
    const updateData = {
      first_name: profileForm.value.first_name,
      last_name: profileForm.value.last_name,
      email: profileForm.value.email,
      username: profileForm.value.username
    }
    await authStore.updateProfile(updateData)
    editMode.value = false
    notificationStore.showSuccess('Профиль успешно обновлен')
  } catch (error) {
    notificationStore.showError('Ошибка при обновлении профиля')
  } finally {
    isLoading.value = false
  }
}

function maskApiKey(key: string): string {
  return `${key.slice(0, 4)}...${key.slice(-4)}`
}

async function fetchExchangeKeys() {
  try {
    const response = await apiClient.get(API_ENDPOINTS.EXCHANGE_KEYS.LIST)
    exchangeKeys.value = response
  } catch (error) {
    notificationStore.showError('Не удалось загрузить API ключи')
  }
}

function openExchangeModal(key: any | null = null) {
  selectedExchangeKey.value = key
  isExchangeModalOpen.value = true
}

function closeExchangeModal() {
  selectedExchangeKey.value = null
  isExchangeModalOpen.value = false
}

async function verifyKey(key: any) {
  try {
    await apiClient.post(API_ENDPOINTS.EXCHANGE_KEYS.VERIFY(key.id))
    notificationStore.showSuccess('API ключ работает корректно')
  } catch (error) {
    notificationStore.showError('Ошибка проверки API ключа')
  }
}

async function deleteKey(key: any) {
  if (!confirm('Вы уверены, что хотите удалить этот ключ?')) return

  try {
    await apiClient.delete(API_ENDPOINTS.EXCHANGE_KEYS.DELETE(key.id))
    await fetchExchangeKeys()
    notificationStore.showSuccess('API ключ успешно удален')
  } catch (error) {
    notificationStore.showError('Ошибка удаления API ключа')
  }
}

async function handleExchangeKeySave() {
  await fetchExchangeKeys()
  closeExchangeModal()
}

// Инициализация
fetchExchangeKeys()
</script>