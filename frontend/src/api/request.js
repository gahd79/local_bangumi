import axios from 'axios'
import { ElMessage } from 'element-plus'

const apiClient = axios.create({
  baseURL: '/api',
  timeout: 30000,  // 30s for potentially slow search/subject-detail calls
  headers: { 'Content-Type': 'application/json' },
})

// Track active requests to avoid duplicate error messages
let errorThrottleTimer = null

// 响应拦截器：提取 data + 统一错误提示
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    const status = error.response?.status
    const detail = error.response?.data?.detail

    // Network error
    if (!status) {
      if (!errorThrottleTimer) {
        ElMessage.error('网络连接失败，请检查后端服务是否启动')
        errorThrottleTimer = setTimeout(() => { errorThrottleTimer = null }, 3000)
      }
      return Promise.reject(error)
    }

    // 404 — only show for direct API calls, not list-empty scenarios
    if (status === 404 && detail) {
      ElMessage.warning(detail)
    } else if (status === 422) {
      const errors = error.response?.data?.errors || []
      ElMessage.warning(errors[0] || '请求参数错误')
    } else if (status >= 500) {
      ElMessage.error(detail || '服务器内部错误，请查看日志')
    } else if (status === 400) {
      ElMessage.warning(detail || '请求参数错误')
    }

    return Promise.reject(error)
  }
)

export default apiClient
