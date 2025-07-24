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
    const { data } = await axios.post('http://localhost:5000/api/auth/login', form)
    localStorage.setItem('token', data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    router.push('/connect')
  } catch (e) { alert(e.response?.data?.msg || e.message) }
}
</script>