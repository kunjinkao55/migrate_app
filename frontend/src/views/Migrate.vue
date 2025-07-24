<template>
  <el-form>
    <el-form-item label="源表"><el-input v-model="form.source_table"/></el-form-item>
    <el-form-item label="目标表"><el-input v-model="form.target_table"/></el-form-item>
    <el-button @click="migrate">开始迁移</el-button>
  </el-form>
</template>
<script setup>
import axios from 'axios'
import { reactive } from 'vue'
const form = reactive({ source_table: '', target_table: '' })
const migrate = async () => {
  await axios.post('http://localhost:5000/api/migrate/table', form)
  alert('迁移完成')
}
</script>