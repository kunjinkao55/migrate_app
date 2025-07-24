import { createRouter, createWebHistory } from 'vue-router'
import Login from '@/views/Login.vue'
import Connect from '@/views/Connect.vue'
import Migrate from '@/views/Migrate.vue'

const routes = [
  { path: '/', redirect: '/login' },
  { path: '/login', component: Login },
  { path: '/connect', component: Connect },
  { path: '/migrate', component: Migrate }
]
export default createRouter({ history: createWebHistory(), routes })