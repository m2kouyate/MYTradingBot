// services/api.ts
import axios, { AxiosError, AxiosInstance, AxiosResponse } from 'axios'
import { API_BASE_URL } from '@/constants/api'
import { useAuthStore } from '@/stores/auth'
import { useNotificationStore } from '@/stores/notification'
import type { ApiError } from '@/types/api'
import { router } from '@/router'

class ApiClient {
  private static instance: ApiClient
  private api: AxiosInstance

  private constructor() {
    this.api = axios.create({
      baseURL: import.meta.env.VITE_API_URL || API_BASE_URL,
      timeout: Number(import.meta.env.VITE_API_TIMEOUT) || 30000,
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
    })

    this.setupInterceptors()
  }

  public static getInstance(): ApiClient {
    if (!ApiClient.instance) {
      ApiClient.instance = new ApiClient()
    }
    return ApiClient.instance
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const authStore = useAuthStore()
        if (authStore.accessToken) {
          config.headers.Authorization = `Bearer ${authStore.accessToken}`
        }
        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.api.interceptors.response.use(
      (response: AxiosResponse) => {
        return response.data
      },
      async (error: AxiosError<ApiError>) => {
        const authStore = useAuthStore()
        const notificationStore = useNotificationStore()
        const originalRequest: any = error.config

        // Handle network errors
        if (!error.response) {
          notificationStore.showError('Ошибка сети. Проверьте подключение к интернету')
          return Promise.reject(error)
        }

        // Handle 401 Unauthorized
        if (error.response.status === 401) {
          // Если это не попытка обновления токена и у нас есть refresh token
          if (!originalRequest._retry && authStore.refreshToken && !originalRequest.url?.includes('/auth/refresh')) {
            originalRequest._retry = true

            try {
              const newToken = await authStore.refreshAccessToken()
              originalRequest.headers.Authorization = `Bearer ${newToken}`
              return this.api(originalRequest)
            } catch (refreshError) {
              // Если не удалось обновить токен, разлогиниваем пользователя
              authStore.clearAuthData()
              router.push('/auth/login')
              notificationStore.showError('Сессия истекла. Пожалуйста, войдите снова')
              return Promise.reject(refreshError)
            }
          }

          // Если это уже повторная попытка или нет refresh token
          if (!authStore.refreshToken || originalRequest._retry) {
            authStore.clearAuthData()
            router.push('/auth/login')
          }
        }

        // Handle 403 Forbidden
        if (error.response.status === 403) {
          notificationStore.showError('У вас нет прав для выполнения этого действия')
        }

        // Handle 422 Validation Error
        if (error.response.status === 422) {
          const errors = error.response.data.errors
          if (errors) {
            Object.values(errors).flat().forEach(error => {
              notificationStore.showError(error as string)
            })
          }
        }

        // Handle other errors
        const errorMessage = this.getErrorMessage(error)
        if (errorMessage && error.response.status !== 422) {
          notificationStore.showError(errorMessage)
        }

        return Promise.reject(error)
      }
    )
  }

  private getErrorMessage(error: AxiosError<ApiError>): string {
    // Приоритет отдаем сообщению от сервера
    if (error.response?.data?.message) {
      return error.response.data.message
    }

    // Если есть ошибки валидации, формируем сообщение из них
    if (error.response?.data?.errors) {
      const errors = error.response.data.errors
      return Object.values(errors).flat().join(', ')
    }

    // Стандартные сообщения по кодам ошибок
    switch (error.response?.status) {
      case 400:
        return 'Неверный запрос. Проверьте введенные данные'
      case 401:
        return 'Необходима авторизация'
      case 403:
        return 'Доступ запрещен'
      case 404:
        return 'Запрашиваемый ресурс не найден'
      case 422:
        return 'Ошибка валидации данных'
      case 429:
        return 'Слишком много запросов. Пожалуйста, подождите'
      case 500:
        return 'Внутренняя ошибка сервера. Попробуйте позже'
      case 503:
        return 'Сервис временно недоступен. Попробуйте позже'
      default:
        return 'Произошла ошибка при выполнении запроса'
    }
  }

  public async get<T>(url: string, config = {}): Promise<T> {
    return this.api.get(url, config)
  }

  public async post<T>(url: string, data = {}, config = {}): Promise<T> {
    return this.api.post(url, data, config)
  }

  public async put<T>(url: string, data = {}, config = {}): Promise<T> {
    return this.api.put(url, data, config)
  }

  public async delete<T>(url: string, config = {}): Promise<T> {
    return this.api.delete(url, config)
  }

  public async patch<T>(url: string, data = {}, config = {}): Promise<T> {
    return this.api.patch(url, data, config)
  }
}

export const apiClient = ApiClient.getInstance()