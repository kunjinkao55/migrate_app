<!-- src/views/Login.vue -->
<template>
  <div>
    <h2>MySQL 登录</h2>
    <form @submit.prevent="login">
      <input v-model="form.host" placeholder="host" />
      <input v-model.number="form.port" placeholder="port" />
      <input v-model="form.user" placeholder="user" />
      <input v-model="form.password" type="password" placeholder="password" />
      <input v-model="form.db" placeholder="database" />
      <button type="submit">登录</button>
    </form>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const form = reactive({ host:'localhost', port:3306, user:'', password:'', db:'' })

const login = async () => {
  try {
    // 【修改】这里不再使用 { data } 解构，而是直接接收返回的响应体
    const responseData = await axios.post('http://localhost:5000/api/auth/login', form)
    
    // 【修改】直接使用 responseData，它就是后端返回的 {"access_token": "..."} 对象
    if (responseData && responseData.access_token) {
      localStorage.setItem('token', responseData.access_token)
      axios.defaults.headers.common['Authorization'] = `Bearer ${responseData.access_token}`
      router.push('/connect')
    } else {
      // 如果登录成功但后端没有返回token，进行提示
      alert('登录失败：响应中未包含 access_token')
    }
  } catch (e) { 
    // 错误处理逻辑保持不变，依然有效
    alert(e.response?.data?.msg || e.message) 
  }
}
</script>
