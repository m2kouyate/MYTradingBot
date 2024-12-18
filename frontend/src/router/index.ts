// router/index.ts
import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/auth',
    component: () => import('@/views/auth/AuthLayout.vue'),
    children: [
      {
        path: 'login',
        name: 'login',
        component: () => import('@/views/auth/LoginView.vue'),
        meta: { requiresGuest: true }
      },
      {
        path: 'register',
        name: 'register',
        component: () => import('@/views/auth/RegisterView.vue'),
        meta: { requiresGuest: true }
      }
    ]
  },
  {
    path: '/',
    component: () => import('@/components/layout/MainLayout.vue'),
    meta: { requiresAuth: true },
    children: [
      {
        path: '',
        name: 'dashboard',
        component: () => import('@/views/DashboardView.vue')
      },
      {
        path: 'strategies',
        name: 'strategies',
        component: () => import('@/views/StrategiesView.vue')
      },
      {
        path: 'trades',
        name: 'trades',
        component: () => import('@/views/TradesView.vue')
      },
      {
        path: 'positions',
        name: 'positions',
        component: () => import('@/views/PositionsView.vue')
      },
      {
        path: 'profile',
        name: 'profile',
        component: () => import('@/views/ProfileView.vue'),
        meta: { requiresAuth: true }
      }
    ]
  },
    // 404 должен быть последним
  {
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('@/views/NotFoundView.vue')
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// Navigation guard
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  const requiresAuth = to.matched.some(record => record.meta.requiresAuth)
  const requiresGuest = to.matched.some(record => record.meta.requiresGuest)

  // Если роут требует авторизации и пользователь не авторизован
  if (requiresAuth && !authStore.isAuthenticated) {
    authStore.clearAuthData() // Очищаем данные авторизации
    next({
      path: '/auth/login',  // Путь к нашему компоненту LoginView
      query: { redirect: to.fullPath }
    })
    return
  }

  // Если роут только для гостей и пользователь авторизован
  if (requiresGuest && authStore.isAuthenticated) {
    next('/')
    return
  }

  next()
})

// export default router
export { router }
