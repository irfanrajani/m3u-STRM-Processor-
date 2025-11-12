import axios from 'axios'
import toast from 'react-hot-toast'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Attach auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Global error handling
api.interceptors.response.use(
  (resp) => resp,
  (error) => {
    const status = error?.response?.status
    const message = error?.response?.data?.detail || error.message || 'Request failed'
    if (status === 401) {
      toast.error('Session expired. Please log in again.')
      localStorage.removeItem('token')
      window.location.href = '/login'
    } else {
      toast.error(message)
    }
    return Promise.reject(error)
  }
)

// Providers
export const getProviders = () => api.get('/providers/')
export const getProvider = (id) => api.get(`/providers/${id}`)
export const createProvider = (data) => api.post('/providers/', data)
export const updateProvider = (id, data) => api.put(`/providers/${id}`, data)
export const deleteProvider = (id) => api.delete(`/providers/${id}`)
export const testProvider = (id) => api.post(`/providers/${id}/test`)
export const syncProvider = (id) => api.post(`/providers/${id}/sync`)
export const syncAllProviders = () => api.post('/providers/sync-all')

// Channels
export const getChannels = (params) => api.get('/channels/', { params })
export const getChannel = (id) => api.get(`/channels/${id}`)
export const getChannelStreams = (id) => api.get(`/channels/${id}/streams`)
export const getCategories = () => api.get('/channels/categories/list')

// VOD
export const getMovies = (params) => api.get('/vod/movies', { params })
export const getSeries = (params) => api.get('/vod/series', { params })
export const getVODStats = () => api.get('/vod/stats')
export const generateSTRM = () => api.post('/vod/generate-strm')

// EPG
export const refreshEPG = (data) => api.post('/epg/refresh', data)
export const getEPGStats = () => api.get('/epg/stats')

// Health
export const triggerHealthCheck = () => api.post('/health/check')
export const getHealthStatus = () => api.get('/health/status')

// Settings
export const getSettings = () => api.get('/settings/')
export const getSetting = (key) => api.get(`/settings/${key}`)
export const updateSetting = (key, data) => api.put(`/settings/${key}`, data)

// STRM Processing
export const processSTRM = (data) => api.post('/strm/process-m3u/', data)

// Favorites
export const getFavorites = () => api.get('/favorites/')
export const addFavorite = (data) => api.post('/favorites/', data)
export const removeFavorite = (id) => api.delete(`/favorites/${id}`)
export const removeFavoriteByChannel = (channelId) => api.delete(`/favorites/channel/${channelId}`)

// Analytics
export const getAnalyticsStats = () => api.get('/analytics/stats')
export const getViewingHistory = (params) => api.get('/analytics/history', { params })
export const getUserActivity = () => api.get('/analytics/user-activity')

// System
export const getSystemConfig = () => api.get('/system/config')
export const updateSystemConfig = (data) => api.put('/system/config', data)
export const getSystemStats = () => api.get('/system/stats')
export const getSystemHealth = () => api.get('/system/health')

export default api
