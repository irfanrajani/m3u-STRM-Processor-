import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || '/api'

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

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

export default api
