// stores/notification.ts
import { defineStore } from 'pinia'
import { ref } from 'vue'

export type NotificationType = 'success' | 'error' | 'warning' | 'info'

export interface Notification {
  id: number
  type: NotificationType
  message: string
  duration?: number
}

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  let nextId = 1

  function showNotification(notification: Omit<Notification, 'id'>) {
    const id = nextId++
    const newNotification = {
      ...notification,
      id,
      duration: notification.duration ?? 5000
    }

    notifications.value.push(newNotification)

    if (newNotification.duration > 0) {
      setTimeout(() => {
        removeNotification(id)
      }, newNotification.duration)
    }
  }

  function removeNotification(id: number): void {
    notifications.value = notifications.value.filter(n => n.id !== id)
  }

  function showSuccess(message: string, duration?: number): void {
    showNotification({ type: 'success', message, duration })
  }

  function showError(message: string, duration?: number): void {
    showNotification({ type: 'error', message, duration })
  }

  function showWarning(message: string, duration?: number): void {
    showNotification({ type: 'warning', message, duration })
  }

  function showInfo(message: string, duration?: number): void {
    showNotification({ type: 'info', message, duration })
  }

  return {
    notifications,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    removeNotification
  }
})