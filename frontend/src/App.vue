<template>
  <div id="app-container">
    <header>
      <div class="logo-wrapper">
        <img alt="Vue logo" class="logo" src="@/assets/logo.svg" width="50" height="50" />
        <span class="app-title">数据库迁移工具</span>
      </div>
      <nav>
        <router-link to="/login">登录</router-link>
        <router-link to="/register">注册</router-link>
        <router-link to="/connect">连接数据库</router-link>
        <router-link to="/migrate">开始迁移</router-link>
      </nav>
    </header>

    <main>
      <!-- 路由匹配到的组件将在这里渲染 -->
      <RouterView />
    </main>
  </div>
</template>

<script setup>
import { RouterLink, RouterView } from 'vue-router'
</script>

<style scoped>
#app-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
}

header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #f8f9fa;
  border-bottom: 1px solid #dee2e6;
}

.logo-wrapper {
  display: flex;
  align-items: center;
}

.app-title {
  margin-left: 1rem;
  font-size: 1.5rem;
  font-weight: 600;
  color: #333;
}

nav {
  display: flex;
  gap: 1.5rem;
}

nav a {
  text-decoration: none;
  color: #007bff;
  font-weight: 500;
  font-size: 1rem;
  transition: color 0.2s;
}

nav a:hover,
nav a.router-link-exact-active {
  color: #0056b3;
  text-decoration: underline;
}

main {
  flex-grow: 1;
  padding: 2rem;
  overflow-y: auto; /* 如果内容超长，允许滚动 */
}
</style>
