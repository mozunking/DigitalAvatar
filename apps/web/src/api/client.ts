import axios from 'axios'
import { ElMessage } from 'element-plus'

let traceCounter = 0

const nextTraceId = () => {
  traceCounter += 1
  return `web-${Date.now()}-${traceCounter}`
}

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL || '/api/v1'

const api = axios.create({
  baseURL: apiBaseUrl
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('digital-avatar-access-token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  if (!config.headers['x-trace-id']) {
    config.headers['x-trace-id'] = nextTraceId()
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config
    const status = error.response?.status
    const errorData = error.response?.data?.error

    if (status === 401 && !originalRequest._retry) {
      const refreshToken = localStorage.getItem('digital-avatar-refresh-token')
      if (refreshToken) {
        originalRequest._retry = true
        try {
          const { data } = await axios.post(`${apiBaseUrl}/auth/refresh`, { refresh_token: refreshToken })
          localStorage.setItem('digital-avatar-access-token', data.access_token)
          localStorage.setItem('digital-avatar-refresh-token', data.refresh_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          localStorage.removeItem('digital-avatar-access-token')
          localStorage.removeItem('digital-avatar-refresh-token')
          window.location.href = '/login'
          return Promise.reject(error)
        }
      }
      localStorage.removeItem('digital-avatar-access-token')
      localStorage.removeItem('digital-avatar-refresh-token')
      if (window.location.pathname !== '/login') {
        window.location.href = '/login'
      }
      return Promise.reject(error)
    }

    if (status === 403) {
      ElMessage.error(errorData?.message || '权限不足')
    } else if (status === 429) {
      ElMessage.warning(errorData?.message || '请求过于频繁，请稍后重试')
    } else if (status && status >= 500) {
      ElMessage.error('服务器错误，请稍后重试')
    }

    return Promise.reject(error)
  }
)

export default api
