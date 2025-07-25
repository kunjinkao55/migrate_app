import { createRouter, createWebHistory } from 'vue-router'
import Login from '../views/Login.vue'
import Register from '../views/Register.vue'
import Connect from '../views/Connect.vue'
import Migrate from '../views/Migrate.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      // 默认路径，自动跳转到登录页
      path: '/',
      redirect: '/login'
    },
    {
      path: '/login',
      name: 'login',
      component: Login
    },
    {
      // 确保注册路由存在且正确
      path: '/register',
      name: 'register',
      component: Register
    },
    {
      path: '/connect',
      name: 'connect',
      component: Connect,
      // 需要登录才能访问
      meta: { requiresAuth: true }
    },
    {
      path: '/migrate',
      name: 'migrate',
      component: Migrate,
      // 需要登录才能访问
      meta: { requiresAuth: true }
    }
  ]
})

// 添加全局路由守卫，实现登录保护
router.beforeEach((to, from, next) => {
  const loggedIn = localStorage.getItem('access_token');

  // 检查目标路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth) && !loggedIn) {
    // 如果需要认证但用户未登录，则跳转到登录页
    next('/login');
  } else {
    // 否则，正常放行
    next();
  }
});

export default router
