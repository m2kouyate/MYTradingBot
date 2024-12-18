import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import { router } from '@/router';
import { apiClient } from '@/services/api';
import type {
  LoginCredentials,
  RegisterCredentials,
  TokenResponse,
  TokenRefreshResponse,
  User,
  SetPassword,
  PasswordResetConfirm,
  ActivationConfirm,
} from '@/types/api';
import { API_ENDPOINTS } from '@/constants/api';
import { useNotificationStore } from './notification';

export const useAuthStore = defineStore('auth', () => {
  const notificationStore = useNotificationStore();

  // State
  const accessToken = ref<string | null>(localStorage.getItem('access_token'));
  const refreshToken = ref<string | null>(localStorage.getItem('refresh_token'));
  const user = ref<User | null>(null);
  const isLoading = ref(false);

  // Getters
  const isAuthenticated = computed(() => !!accessToken.value);
  const userFullName = computed(() => {
    if (!user.value) return '';
    return user.value.first_name && user.value.last_name
      ? `${user.value.first_name} ${user.value.last_name}`
      : user.value.username;
  });

  // Actions
  async function register(credentials: RegisterCredentials) {
    try {
      isLoading.value = true;
      await apiClient.post(API_ENDPOINTS.AUTH.REGISTER, credentials);
      notificationStore.showSuccess('Регистрация успешна. Проверьте email для активации аккаунта');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка при регистрации');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function login(credentials: LoginCredentials) {
    try {
      isLoading.value = true;
      const response = await apiClient.post<TokenResponse>(API_ENDPOINTS.AUTH.LOGIN, credentials);

      // Сохраняем токены в localStorage
      accessToken.value = response.access;
      refreshToken.value = response.refresh;
      localStorage.setItem('access_token', response.access);
      localStorage.setItem('refresh_token', response.refresh);

      // Загружаем профиль пользователя
      await fetchUserProfile();

      notificationStore.showSuccess('Успешный вход в систему');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка входа в систему');
      return false;
    } finally {
      isLoading.value = false;
    }
  }

  async function refreshAccessToken() {
    try {
      if (!refreshToken.value) {
        throw new Error('No refresh token available');
      }

      const response = await apiClient.post<TokenRefreshResponse>(API_ENDPOINTS.AUTH.REFRESH, {
        refresh: refreshToken.value,
      });

      accessToken.value = response.access;
      localStorage.setItem('access_token', response.access);

      return response.access;
    } catch (error) {
      clearAuthData();
      throw error;
    }
  }

  async function logout() {
  try {
    isLoading.value = true;

    // LOGOUT endpoint отсутствует в djoser, так что просто очищаем данные
    clearAuthData();

    // Исправляем путь редиректа на /auth/login вместо /jwt/create
    router.push('/auth/login');

    notificationStore.showSuccess('Вы успешно вышли из системы');
  } catch (error) {
    console.error('Ошибка при выходе:', error);
    notificationStore.showError('Ошибка при выходе');
  } finally {
    isLoading.value = false;
  }
}

  async function fetchUserProfile() {
    try {
      const response = await apiClient.get<User>(API_ENDPOINTS.AUTH.PROFILE);
      user.value = response;
    } catch (error) {
      console.error('Error fetching user profile:', error);
    }
  }

  async function activateAccount(data: ActivationConfirm) {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.ACTIVATION, data);
      notificationStore.showSuccess('Аккаунт успешно активирован');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка при активации аккаунта');
      return false;
    }
  }

  async function resetPassword(email: string) {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD, { email });
      notificationStore.showSuccess('Инструкции по сбросу пароля отправлены на email');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка при запросе сброса пароля');
      return false;
    }
  }

  async function resetPasswordConfirm(data: PasswordResetConfirm) {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.RESET_PASSWORD_CONFIRM, data);
      notificationStore.showSuccess('Пароль успешно изменен');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка при изменении пароля');
      return false;
    }
  }

  async function changePassword(data: SetPassword) {
    try {
      await apiClient.post(API_ENDPOINTS.AUTH.SET_PASSWORD, data);
      notificationStore.showSuccess('Пароль успешно изменен');
      return true;
    } catch (error) {
      notificationStore.showError('Ошибка при изменении пароля');
      return false;
    }
  }

  async function updateProfile(data: Partial<User>) {
    try {
      isLoading.value = true
      const response = await apiClient.patch<User>(API_ENDPOINTS.AUTH.PROFILE, data)
      // Обновляем все поля пользователя, а не заменяем объект целиком
      user.value = {
        ...user.value,
        ...response
      }
      await fetchUserProfile() // Добавляем повторную загрузку профиля
      notificationStore.showSuccess('Профиль успешно обновлен')
      return true
    } catch (error) {
      notificationStore.showError('Ошибка при обновлении профиля')
      return false
    } finally {
      isLoading.value = false
    }
  }

  function clearAuthData() {
    accessToken.value = null;
    refreshToken.value = null;
    user.value = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  // Initialize
  if (accessToken.value) {
    fetchUserProfile();
  }

  return {
    // State
    accessToken,
    refreshToken,
    user,
    isLoading,
    // Getters
    isAuthenticated,
    userFullName,
    // Actions
    register,
    login,
    logout,
    refreshAccessToken,
    fetchUserProfile,
    activateAccount,
    resetPassword,
    resetPasswordConfirm,
    changePassword,
    updateProfile,
    clearAuthData,
  };
});
