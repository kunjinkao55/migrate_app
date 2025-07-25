<!-- <template>
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
</script> -->

<template>
  <div class="connect-container">
    <h2>连接到数据库</h2>
    <el-form>
      <el-form-item label="主机">
        <el-input v-model="credentials.host"></el-input>
      </el-form-item>
      <el-form-item label="端口">
        <el-input v-model="credentials.port"></el-input>
      </el-form-item>
      <el-form-item label="用户">
        <el-input v-model="credentials.user"></el-input>
      </el-form-item>
      <el-form-item label="密码">
        <el-input v-model="credentials.pwd" type="password"></el-input>
      </el-form-item>
      <el-form-item label="数据库">
        <el-input v-model="credentials.db"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="connectToDb">连接</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { ElMessage } from 'element-plus';
import apiClient from '@/api'; // 导入 apiClient

const router = useRouter();
const credentials = ref({
  host: 'localhost',
  port: 3306,
  user: 'root',
  pwd: '',
  db: ''
});

async function connectToDb() {
  try {
    const response = await apiClient.post('/migrate/connect', credentials.value);
    
    // 检查后端的成功消息
    if (response.status === 200) {
      ElMessage.success('连接成功！即将跳转到迁移页面...');
      setTimeout(() => {
         router.push('/migrate');
      }, 1500);
    }
  } catch (error) {
    // 错误已由 apiClient 的响应拦截器统一处理
    console.error('连接失败:', error);
  }
}
</script>

<style scoped>
.connect-container {
  max-width: 500px;
  margin: 50px auto;
  padding: 20px;
  border: 1px solid #ccc;
  border-radius: 10px;
}
</style>
