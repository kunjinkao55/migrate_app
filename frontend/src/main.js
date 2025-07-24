import "./assets/main.css";
import {createApp} from "vue";
import {createPinia} from "pinia";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import App from "./App.vue";
import router from "./router";
import axios from 'axios'

const token = localStorage.getItem('token')
if (token) axios.defaults.headers.common['Authorization'] = `Bearer ${token}`


const login = async () => {
  try {
    const res = await axios.post('http://localhost:5000/api/auth/login', form)
    const data = res.data || {}          // 👈 兜底
    if (!data.access_token) {
      alert('登录失败：' + data.msg || '无 token')
      return
    }
    localStorage.setItem('token', data.access_token)
    axios.defaults.headers.common['Authorization'] = `Bearer ${data.access_token}`
    router.push('/connect')
  } catch (e) {
    alert(e.response?.data?.msg || '网络错误')
  }
}

/* 2. 拦截 401 → 踢回登录页 */
axios.interceptors.response.use(
  res => res.data,
  err => {
    if (err.response?.status === 401) {
      localStorage.removeItem('token');
      router.replace('/login');
    }
    return Promise.reject(err);
  }
);

const app = createApp(App);
app.use(createPinia());
app.use(router);
app.use(ElementPlus);
app.mount("#app");
