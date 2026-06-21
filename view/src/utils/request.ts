import axios from 'axios'
import type { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { ElMessage } from 'element-plus'
import type { ApiResponse } from '@/types/models'

// In mock mode the MSW service worker is registered under Vite's `base`
// (`/networth/`), so its scope only covers `/networth/*`. Requests to `/api/*`
// fall outside the scope, miss MSW entirely, and hit the (non-running) dev
// proxy target. Align the baseURL to land inside the worker's scope; handlers
// use `*/<resource>` wildcards so they still match.
const baseURL =
  import.meta.env.VITE_USE_MOCK === 'true'
    ? `${import.meta.env.BASE_URL}api`
    : import.meta.env.VITE_API_BASE_URL || '/api'

const service: AxiosInstance = axios.create({
  baseURL,
  timeout: 10000,
})

service.interceptors.request.use(
  (config) => config,
  (error) => Promise.reject(error),
)

service.interceptors.response.use(
  (response: AxiosResponse<ApiResponse<unknown>>) => {
    const env = response.data
    if (env.status === 1) return response
    ElMessage.error(env.msg || '請求失敗')
    return Promise.reject(new Error(env.msg || 'Error'))
  },
  (error) => {
    const msg = error.response?.data?.msg || error.message || '網路錯誤'
    ElMessage.error(msg)
    return Promise.reject(error)
  },
)

const request = {
  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await service.get<ApiResponse<T>>(url, config)
    return res.data.data
  },
  async post<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await service.post<ApiResponse<T>>(url, data, config)
    return res.data.data
  },
  async put<T>(url: string, data?: unknown, config?: AxiosRequestConfig): Promise<T> {
    const res = await service.put<ApiResponse<T>>(url, data, config)
    return res.data.data
  },
  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const res = await service.delete<ApiResponse<T>>(url, config)
    return res.data.data
  },
}

export default request
