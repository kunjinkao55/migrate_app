import {createRouter, createWebHistory} from "vue-router";
import Login from "@/views/Login.vue";
import Register from "@/views/Register.vue";
import Connect from "@/views/Connect.vue";
import Migrate from "@/views/Migrate.vue";

const routes = [
  {path: "/", redirect: "/login"},
  {path: "/login", component: Login},
  {path: "/register", component: Register},
  {path: "/connect", component: Connect},
  {path: "/migrate", component: Migrate},
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

// 添加路由守卫
router.beforeEach((to, from, next) => {
  const publicPages = ["/login", "/register"];
  const authRequired = !publicPages.includes(to.path);
  const token = localStorage.getItem("token");

  if (authRequired && !token) {
    return next("/login");
  }
  next();
});

export default router;
