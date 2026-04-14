import axios from 'axios'
import { ElMessage } from 'element-plus'
import { authTokenStorage } from './authStorage'

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
  const token = authTokenStorage.getAccessToken()
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
      const refreshToken = authTokenStorage.getRefreshToken()
      if (refreshToken) {
        originalRequest._retry = true
        try {
          const { data } = await axios.post(`${apiBaseUrl}/auth/refresh`, { refresh_token: refreshToken })
          authTokenStorage.setTokens(data.access_token, data.refresh_token)
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`
          return api(originalRequest)
        } catch {
          authTokenStorage.clear()
          window.location.href = '/login'
          return Promise.reject(error)
        }
      }
      authTokenStorage.clear()
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
