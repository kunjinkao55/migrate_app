<template>
  <div class="migrate-container">
    <h2>数据库迁移 (推送-拉取模式)</h2>
    
    <el-card class="box-card">
      <template #header>
        <div class="card-header">
          <span>第一步：推送数据到中转区</span>
          <el-button class="button" text @click="fetchTables">刷新表列表</el-button>
        </div>
      </template>
      <el-alert type="info" show-icon :closable="false" style="margin-bottom: 20px;">
        请先在“连接数据库”页面连接到您的 **源数据库 (甲方)**。
      </el-alert>
      <el-form>
        <el-form-item label="选择源表">
          <el-select v-model="sourceTable" placeholder="请选择要推送的源表">
            <el-option v-for="table in tables" :key="table" :label="table" :value="table"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="pushData">推送数据</el-button>
        </el-form-item>
      </el-form>
      <div v-if="taskId" class="task-id-display">
        <el-alert title="推送成功！" type="success" show-icon>
          <p>请复制并妥善保管以下任务ID，并将其交给数据接收方 (乙方)。</p>
          <strong>{{ taskId }}</strong>
        </el-alert>
      </div>
    </el-card>

    <el-card class="box-card" style="margin-top: 30px;">
      <template #header>
        <div class="card-header">
          <span>第二步：从中转区拉取数据</span>
           <el-button class="button" text @click="fetchTables">刷新表列表</el-button>
        </div>
      </template>
      <el-alert type="info" show-icon :closable="false" style="margin-bottom: 20px;">
         请先在“连接数据库”页面连接到您的 **目标数据库 (乙方)**。
      </el-alert>
      <el-form>
        <el-form-item label="输入任务ID">
          <el-input v-model="taskIdToPull" placeholder="请输入数据推送方提供的任务ID"></el-input>
        </el-form-item>
        <el-form-item label="选择目标表">
          <el-select v-model="targetTable" placeholder="请选择要接收数据的目标表">
             <el-option v-for="table in tables" :key="table" :label="table" :value="table"></el-option>
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="success" @click="pullData">拉取数据</el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import apiClient from '@/api';

const tables = ref([]);
const sourceTable = ref('');
const targetTable = ref('');
const taskId = ref('');
const taskIdToPull = ref('');

// 获取当前连接的数据库的表列表
async function fetchTables() {
  try {
    const response = await apiClient.get('/migrate/tables');
    tables.value = response.data.tables;
    if (tables.value.length === 0) {
        ElMessage.warning('当前数据库中没有找到任何表，请确认连接信息是否正确。');
    } else {
        ElMessage.success('表列表已刷新！');
    }
  } catch (error) {
    console.error('获取表列表失败:', error);
  }
}

// 推送数据
async function pushData() {
  if (!sourceTable.value) {
    ElMessage.warning('请选择源表！');
    return;
  }
  try {
    const response = await apiClient.post('/migrate/push', {
      source_table: sourceTable.value,
    });
    if (response.status === 200) {
      taskId.value = response.data.task_id;
      ElMessage.success(response.data.msg || '推送成功！');
    }
  } catch (error) {
    console.error('推送失败:', error);
  }
}

// 拉取数据
async function pullData() {
  if (!taskIdToPull.value || !targetTable.value) {
    ElMessage.warning('请输入任务ID并选择目标表！');
    return;
  }
  try {
    const response = await apiClient.post('/migrate/pull', {
      task_id: taskIdToPull.value,
      target_table: targetTable.value,
    });
    if (response.status === 200) {
      ElMessage.success(response.data.msg || '拉取成功！');
    }
  } catch (error) {
    console.error('拉取失败:', error);
  }
}

// 组件加载时自动获取一次表列表
onMounted(() => {
  fetchTables();
});
</script>

<style scoped>
.migrate-container {
  max-width: 800px;
  margin: 50px auto;
}
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.task-id-display {
    margin-top: 20px;
    padding: 10px;
    border: 1px solid #e9e9eb;
    border-radius: 4px;
}
</style>