<template>
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
</script>
