<!-- <template>
  <div class="register">
    <el-card class="register-card">
      <h2>注册</h2>
      <el-form :model="form" label-width="80px">
        <el-form-item label="用户名">
          <el-input v-model="form.username" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input v-model="form.password" type="password" />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="register">注册</el-button>
          <el-button @click="$router.push('/login')">返回登录</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import {reactive} from "vue";
import {useRouter} from "vue-router";
import axios from "axios";
import {ElMessage} from "element-plus";

const router = useRouter();
const form = reactive({username: "", password: ""});

const register = async () => {
  try {
    const res = await axios.post(
      "http://localhost:5000/api/auth/register",
      form
    );
    ElMessage.success(res.msg || "注册成功");
    router.push("/login");
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || "注册失败");
  }
};
</script>

<style scoped>
.register {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.register-card {
  width: 400px;
}
</style> -->

<template>
  <div class="register-container">
    <h2>注册</h2>
    <el-form @submit.prevent="handleRegister">
      <el-form-item label="用户名">
        <el-input v-model="username" placeholder="请输入用户名"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="password" type="password" placeholder="请输入密码"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleRegister">注册</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import apiClient from '@/api'; // 导入 apiClient

const username = ref('');
const password = ref('');
const router = useRouter();

async function handleRegister() {
  try {
    const response = await apiClient.post('/auth/register', {
      username: username.value,
      password: password.value,
    });

    // 检查后端返回的成功消息
    if (response.status === 201) {
       ElMessage.success('注册成功！正在跳转到登录页面...');
       setTimeout(() => {
         router.push('/login');
       }, 1500);
    }
  } catch (error) {
    // 错误已由 apiClient 的响应拦截器统一处理
    console.error('注册失败:', error);
  }
}
</script>

<style scoped>
.register-container {
  max-width: 400px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
}
</style>
