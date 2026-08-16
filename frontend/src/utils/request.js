import axios from 'axios'
import { ElMessage } from 'element-plus'
import router from '@/router'

const request = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000/api',
  timeout: 30000,
})

// 请求拦截器：自动携带 token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理错误
request.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail
    const silent = error.config?.silent

    if (status === 401) {
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      router.push('/login')
      if (!silent) ElMessage.error('登录已过期，请重新登录')
    } else if (!silent) {
      if (status === 403) {
        ElMessage.error(detail || '权限不足')
      } else if (status === 404) {
        ElMessage.error(detail || '资源不存在')
      } else if (status === 422) {
        const msg = Array.isArray(detail) ? detail[0]?.msg : detail
        ElMessage.error(msg || '请求参数错误')
      } else if (status >= 500) {
        ElMessage.error(detail || '服务器内部错误')
      } else {
        ElMessage.error(detail || '请求失败')
      }
    }
    return Promise.reject(error)
  }
)

export default request
