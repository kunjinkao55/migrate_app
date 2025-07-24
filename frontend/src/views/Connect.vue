<template>
  <el-form>
    <el-form-item label="Host"><el-input v-model="form.host"/></el-form-item>
    <el-form-item label="Port"><el-input v-model.number="form.port"/></el-form-item>
    <el-form-item label="用户名"><el-input v-model="form.user"/></el-form-item>
    <el-form-item label="密码"><el-input type="password" v-model="form.pwd"/></el-form-item>
    <el-form-item label="数据库"><el-input v-model="form.db"/></el-form-item>
    <el-button @click="connect">连接</el-button>
  </el-form>
</template>
<script setup>
import axios from 'axios'
import { reactive } from 'vue'
import { useRouter } from 'vue-router'
const form = reactive({ host: 'localhost', port: 3306, user: 'root', pwd: '', db: 'source' })
const router = useRouter()
const connect = async () => {
  await axios.post('http://localhost:5000/api/migrate/connect', form)
  router.push('/migrate')
}
</script>