import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Connect from '@/views/Connect.vue'
import Migrate from '@/views/Migrate.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/connect',
      name: 'connect',
      component: Connect,
      meta: { requiresAuth: true }
    },
    {
      path: '/migrate',
      name: 'migrate',
      component: Migrate,
      meta: { requiresAuth: true }
    }
  ]
})

// --- 修改这里 ---
router.beforeEach((to, from, next) => {
  // 将 'token' 修改为 'access_token'
  const accessToken = localStorage.getItem('access_token');
  if (to.meta.requiresAuth && !accessToken) {
    next('/login');
  } else {
    next();
  }
});

export default router