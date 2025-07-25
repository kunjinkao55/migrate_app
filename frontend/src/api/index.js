import axios from 'axios';
import { ElMessage } from 'element-plus';

// 创建一个 Axios 实例，预先配置好后端地址和关键的跨域选项
const apiClient = axios.create({
  baseURL: 'http://localhost:5000/api', // 你的后端 API 基础地址
  withCredentials: true, // 关键！允许跨域请求携带 cookie
});

// 添加一个请求拦截器，在每个请求发出前自动附加上 JWT token
apiClient.interceptors.request.use(config => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, error => {
  return Promise.reject(error);
});


// 添加一个响应拦截器，用于统一处理错误
apiClient.interceptors.response.use(
  response => {
    // 如果响应成功，直接返回响应数据
    return response;
  },
  error => {
    // 如果发生错误，在这里统一处理
    let errorMessage = '发生未知错误';
    if (error.response) {
      // 服务器返回了错误状态码
      errorMessage = error.response.data.msg || `服务器错误: ${error.response.status}`;
    } else if (error.request) {
      // 请求已发出，但没有收到响应（例如，网络错误）
      errorMessage = '无法连接到服务器，请检查您的网络或后端服务是否正在运行。';
    } else {
      // 设置请求时发生了一些事情，触发了一个错误
      errorMessage = error.message;
    }
    
    // 使用 Element Plus 的 ElMessage 组件弹出错误提示
    ElMessage.error(errorMessage);
    
    // 返回一个被拒绝的 Promise，以便调用方可以继续处理错误
    return Promise.reject(error);
  }
);


export default apiClient;

