<!-- <template>
  <el-card>
    <el-form :model="form" label-width="120px">
      <el-form-item label="源表">
        <el-input v-model="form.source_table" />
      </el-form-item>
      <el-form-item label="目标表">
        <el-input v-model="form.target_table" />
      </el-form-item>
      <el-button type="primary" @click="migrate">开始迁移</el-button>
    </el-form>
  </el-card>
</template>

<script setup>
import axios from "axios";
import {reactive} from "vue";
import {ElMessage} from "element-plus";

const form = reactive({
  source_table: "",
  target_table: "",
});

const migrate = async () => {
  try {
    const res = await axios.post(
      "http://localhost:5000/api/migrate/table",
      form
    );
    ElMessage.success(res.msg || "迁移成功");
  } catch (e) {
    ElMessage.error(e.response?.data?.msg || "迁移失败");
  }
};
</script> -->
<template>
  <div class="migrate-container">
    <h2>数据库迁移</h2>
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>选择表进行迁移</span>
          <el-button class="button" text @click="fetchTables">刷新表列表</el-button>
        </div>
      </template>
      <el-form>
        <el-form-item label="源表">
          <el-select v-model="sourceTable" placeholder="请选择源表">
            <el-option v-for="table in tables" :key="table" :label="table" :value="table"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item label="目标表">
          <el-select v-model="targetTable" placeholder="请选择目标表">
             <el-option v-for="table in tables" :key="table" :label="table" :value="table"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="startMigration">开始迁移</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api'; // 导入 apiClient

const tables = ref([]);
const sourceTable = ref('');
const targetTable = ref('');

async function fetchTables() {
  try {
    const response = await apiClient.get('/migrate/tables');
    tables.value = response.data.tables;
    ElMessage.success('表列表已刷新！');
  } catch (error) {
    // 错误已由 apiClient 的响应拦截器统一处理
    console.error('获取表列表失败:', error);
  }
}

async function startMigration() {
  if (!sourceTable.value || !targetTable.value) {
    ElMessage.warning('请选择源表和目标表！');
    return;
  }
  
  try {
    const response = await apiClient.post('/migrate/table', {
      source_table: sourceTable.value,
      target_table: targetTable.value
    });
    // 检查后端的成功消息
    if (response.status === 200) {
      ElMessage.success(response.data.msg || '迁移成功！');
    }
  } catch (error) {
     // 错误已由 apiClient 的响应拦截器统一处理
    console.error('迁移失败:', error);
  }
}

// 组件加载时自动获取一次表列表
onMounted(() => {
  fetchTables();
});
</script>

<style scoped>
.migrate-container {
  max-width: 600px;
  margin: 50px auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

