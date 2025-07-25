<template>
  <div class="login-container">
    <h2>登录</h2>
    <el-form @submit.prevent="handleLogin">
      <el-form-item label="用户名">
        <el-input v-model="username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleLogin" class="login-button">登录</el-button>
      </el-form-item>
      
      <!-- 新增的注册链接 -->
      <div class="register-link">
        还没有账号？ <router-link to="/register">立即注册</router-link>
      </div>

    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import apiClient from '@/api'; 

const username = ref('');
const password = ref('');
const router = useRouter();

async function handleLogin() {
  try {
    const response = await apiClient.post('/auth/login', {
      username: username.value,
      password: password.value,
    });
    console.log('后端返回的完整响应:', response);
    console.log('后端返回的 data 部分:', response.data);
    if (response.data.access_token) {
      localStorage.setItem('access_token', response.data.access_token);
      router.push('/connect');
    }
  } catch (error) {
    console.error('登录失败:', error);
  }
}
</script>

<style scoped>
.login-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px 30px;
  border: 1px solid #dcdfe6;
  border-radius: 10px;
  box-shadow: 0 2px 12px 0 rgba(255, 255, 255, 0.1);
}

.login-button {
  width: 100%;
}

.register-link {
  margin-top: 15px;
  text-align: center;
  font-size: 14px;
}

.register-link a {
  color: #409eff;
  text-decoration: none;
}
.register-link a:hover {
  text-decoration: underline;
}
</style>
