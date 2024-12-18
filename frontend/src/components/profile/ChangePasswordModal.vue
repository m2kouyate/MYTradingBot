<template>
  <TransitionRoot appear show as="template">
    <Dialog as="div" @close="closeModal" class="relative z-50">
      <div class="fixed inset-0 bg-black/30" />

      <div class="fixed inset-0 overflow-y-auto">
        <div class="flex min-h-full items-center justify-center p-4">
          <DialogPanel class="w-full max-w-md transform overflow-hidden rounded-lg bg-white p-6 shadow-xl transition-all">
            <div class="flex justify-between items-start">
              <DialogTitle as="h3" class="text-lg font-medium leading-6 text-gray-900">
                Смена пароля
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
                    Текущий пароль
                  </label>
                  <div class="mt-1 relative">
                    <input
                      :type="showCurrentPassword ? 'text' : 'password'"
                      v-model="form.current_password"
                      required
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 pr-10 sm:text-sm"
                      :class="{ 'border-red-300': errors.current_password }"
                    />
                    <button
                      type="button"
                      @click="showCurrentPassword = !showCurrentPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      <EyeIcon v-if="!showCurrentPassword" class="h-5 w-5 text-gray-400" />
                      <EyeOffIcon v-else class="h-5 w-5 text-gray-400" />
                    </button>
                  </div>
                  <p v-if="errors.current_password" class="mt-1 text-sm text-red-600">
                    {{ errors.current_password }}
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    Новый пароль
                  </label>
                  <div class="mt-1 relative">
                    <input
                      :type="showNewPassword ? 'text' : 'password'"
                      v-model="form.new_password"
                      required
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 pr-10 sm:text-sm"
                      :class="{ 'border-red-300': errors.new_password }"
                    />
                    <button
                      type="button"
                      @click="showNewPassword = !showNewPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      <EyeIcon v-if="!showNewPassword" class="h-5 w-5 text-gray-400" />
                      <EyeOffIcon v-else class="h-5 w-5 text-gray-400" />
                    </button>
                  </div>
                  <p v-if="errors.new_password" class="mt-1 text-sm text-red-600">
                    {{ errors.new_password }}
                  </p>
                </div>

                <div>
                  <label class="block text-sm font-medium text-gray-700">
                    Подтверждение нового пароля
                  </label>
                  <div class="mt-1 relative">
                    <input
                      :type="showConfirmPassword ? 'text' : 'password'"
                      v-model="form.re_new_password"
                      required
                      class="block w-full rounded-md border-gray-300 shadow-sm focus:border-primary-500 focus:ring-primary-500 pr-10 sm:text-sm"
                      :class="{ 'border-red-300': errors.re_new_password }"
                    />
                    <button
                      type="button"
                      @click="showConfirmPassword = !showConfirmPassword"
                      class="absolute inset-y-0 right-0 pr-3 flex items-center"
                    >
                      <EyeIcon v-if="!showConfirmPassword" class="h-5 w-5 text-gray-400" />
                      <EyeOffIcon v-else class="h-5 w-5 text-gray-400" />
                    </button>
                  </div>
                  <p v-if="errors.re_new_password" class="mt-1 text-sm text-red-600">
                    {{ errors.re_new_password }}
                  </p>
                </div>
              </div>

              <div class="mt-6">
                <button
                  type="submit"
                  :disabled="isLoading"
                  class="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
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
import { X, Loader, Eye as EyeIcon, EyeOff as EyeOffIcon } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import { apiClient } from '@/services/api'
import { API_ENDPOINTS } from '@/constants/api'

const emit = defineEmits<{
  close: []
}>()

const authStore = useAuthStore()
const notificationStore = useNotificationStore()
const isLoading = ref(false)
const showCurrentPassword = ref(false)
const showNewPassword = ref(false)
const showConfirmPassword = ref(false)

const form = ref({
  current_password: '',
  new_password: '',
  re_new_password: ''
})

const errors = ref({
  current_password: '',
  new_password: '',
  re_new_password: ''
})

function resetErrors() {
  errors.value = {
    current_password: '',
    new_password: '',
    re_new_password: ''
  }
}

async function handleSubmit() {
  resetErrors()

  if (form.value.new_password !== form.value.re_new_password) {
    errors.value.re_new_password = 'Пароли не совпадают'
    return
  }

  if (form.value.new_password.length < 8) {
    errors.value.new_password = 'Пароль должен содержать минимум 8 символов'
    return
  }

  isLoading.value = true
  try {
    await apiClient.post(API_ENDPOINTS.AUTH.SET_PASSWORD, {
      current_password: form.value.current_password,
      new_password: form.value.new_password,
      re_new_password: form.value.re_new_password
    })

    notificationStore.showSuccess('Пароль успешно изменен')
    closeModal()
  } catch (error: any) {
    const responseData = error.response?.data
    if (responseData) {
      // Обработка ошибок от API
      if (responseData.current_password) {
        errors.value.current_password = responseData.current_password[0]
      }
      if (responseData.new_password) {
        errors.value.new_password = responseData.new_password[0]
      }
      if (responseData.re_new_password) {
        errors.value.re_new_password = responseData.re_new_password[0]
      }
      if (responseData.non_field_errors) {
        notificationStore.showError(responseData.non_field_errors[0])
      }
    } else {
      notificationStore.showError('Ошибка при изменении пароля')
    }
  } finally {
    isLoading.value = false
  }
}

function closeModal() {
  form.value = {
    current_password: '',
    new_password: '',
    re_new_password: ''
  }
  resetErrors()
  emit('close')
}
</script>