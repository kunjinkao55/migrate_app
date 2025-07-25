import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Register from '@/views/Register.vue'
import Connect from '@/views/Connect.vue'
// 这里的 Migrate.vue 应该是已经包含了“推送”和“拉取”功能的新组件
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
      component: Migrate, // 此路由指向重构后的迁移页面
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const token = localStorage.getItem('token')
  if (to.meta.requiresAuth && !token) {
    next('/login')
  } else {
    next()
  }
})

export default router