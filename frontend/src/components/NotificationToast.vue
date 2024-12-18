// components/NotificationToast.vue
<template>
  <div class="fixed bottom-4 right-4 z-50 space-y-2">
    <TransitionGroup name="notification">
      <div
        v-for="notification in notifications"
        :key="notification.id"
        class="p-4 rounded-lg shadow-lg max-w-md"
        :class="getNotificationClass(notification.type)"
      >
        <div class="flex items-center justify-between">
          <p class="text-sm">{{ notification.message }}</p>
          <button
            @click="removeNotification(notification.id)"
            class="ml-4 text-current opacity-50 hover:opacity-100"
          >
            <XMarkIcon class="h-5 w-5" />
          </button>
        </div>
      </div>
    </TransitionGroup>
  </div>
</template>

<script setup lang="ts">
import { XMarkIcon } from '@heroicons/vue/24/outline'
import { useNotificationStore } from '@/stores/notification'
import { computed } from 'vue'

const notificationStore = useNotificationStore()

const notifications = computed(() => notificationStore.notifications)

const removeNotification = (id: number) => {
  notificationStore.removeNotification(id)
}

const getNotificationClass = (type: string) => {
  switch (type) {
    case 'success':
      return 'bg-green-100 text-green-800'
    case 'error':
      return 'bg-red-100 text-red-800'
    case 'warning':
      return 'bg-yellow-100 text-yellow-800'
    case 'info':
      return 'bg-blue-100 text-blue-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}
</script>

<style scoped>
.notification-enter-active,
.notification-leave-active {
  transition: all 0.3s ease;
}

.notification-enter-from {
  opacity: 0;
  transform: translateX(30px);
}

.notification-leave-to {
  opacity: 0;
  transform: translateX(30px);
}
</style>