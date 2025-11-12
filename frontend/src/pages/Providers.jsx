import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProviders, createProvider, updateProvider, deleteProvider, testProvider, syncProvider } from '../services/api'
import { Plus, Trash2, Edit3, Activity, RefreshCw, Tv, Film, Clock, ToggleLeft, ToggleRight } from 'lucide-react'
import AddProviderModal from '../components/AddProviderModal'
import EditProviderModal from '../components/EditProviderModal'
import toast from 'react-hot-toast'

export default function Providers() {
  const queryClient = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)
  const [showEditModal, setShowEditModal] = useState(false)
  const [selectedProvider, setSelectedProvider] = useState(null)
  const [testingIds, setTestingIds] = useState(new Set())
  const [syncingIds, setSyncingIds] = useState(new Set())

  const { data, isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
      setShowAddModal(false)
      toast.success('Provider created successfully')
    },
    onError: () => {
      toast.error('Failed to create provider')
    }
  })

  const updateMutation = useMutation({
    mutationFn: ({ id, data }) => updateProvider(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
      setShowEditModal(false)
      toast.success('Provider updated successfully')
    },
    onError: () => {
      toast.error('Failed to update provider')
    }
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
      toast.success('Provider deleted successfully')
    },
    onError: () => {
      toast.error('Failed to delete provider')
    }
  })

  const testMutation = useMutation({
    mutationFn: testProvider,
    onSuccess: (data) => {
      toast.success(data?.message || 'Connection test successful')
    },
    onError: (error) => {
      toast.error(error?.response?.data?.detail || 'Connection test failed')
    }
  })

  const syncMutation = useMutation({
    mutationFn: syncProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
      toast.success('Provider synced successfully')
    },
    onError: () => {
      toast.error('Failed to sync provider')
    }
  })

  const handleToggleEnabled = async (provider) => {
    // Optimistic update
    const newEnabled = !provider.enabled
    queryClient.setQueryData(['providers'], (old) => ({
      ...old,
      data: old.data.map(p => p.id === provider.id ? { ...p, enabled: newEnabled } : p)
    }))
    
    try {
      await updateProvider(provider.id, { ...provider, enabled: newEnabled })
      toast.success(`Provider ${newEnabled ? 'enabled' : 'disabled'}`)
    } catch (error) {
      // Revert on error
      queryClient.invalidateQueries(['providers'])
      toast.error('Failed to update provider')
    }
  }

  const handleTest = async (id) => {
    setTestingIds(prev => new Set([...prev, id]))
    try {
      await testMutation.mutateAsync(id)
    } finally {
      setTestingIds(prev => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleSync = async (id) => {
    setSyncingIds(prev => new Set([...prev, id]))
    try {
      await syncMutation.mutateAsync(id)
    } finally {
      setSyncingIds(prev => {
        const next = new Set(prev)
        next.delete(id)
        return next
      })
    }
  }

  const handleEdit = (provider) => {
    setSelectedProvider(provider)
    setShowEditModal(true)
  }

  const handleDelete = (id) => {
    if (window.confirm('Are you sure you want to delete this provider? This action cannot be undone.')) {
      deleteMutation.mutate(id)
    }
  }

  const formatRelativeTime = (dateString) => {
    if (!dateString) return 'Never'
    const date = new Date(dateString)
    const now = new Date()
    const diffMs = now - date
    const diffMins = Math.floor(diffMs / 60000)
    
    if (diffMins < 1) return 'Just now'
    if (diffMins < 60) return `${diffMins}m ago`
    const diffHours = Math.floor(diffMins / 60)
    if (diffHours < 24) return `${diffHours}h ago`
    const diffDays = Math.floor(diffHours / 24)
    return `${diffDays}d ago`
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading providers...</p>
        </div>
      </div>
    )
  }

  const providers = (data?.data || []).sort((a, b) => (b.priority || 0) - (a.priority || 0))

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8 max-w-7xl mx-auto">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <div>
          <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent">
            Providers
          </h1>
          <p className="mt-2 text-sm text-gray-600">
            Manage your IPTV and M3U providers
          </p>
        </div>
        <button
          onClick={() => setShowAddModal(true)}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2.5 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-700 hover:to-accent-700 transition-all duration-200 shadow-glow-brand"
        >
          <Plus className="mr-2 h-5 w-5" />
          Add Provider
        </button>
      </div>

      {providers.length === 0 ? (
        <div className="text-center py-12 bg-white rounded-lg shadow">
          <Tv className="mx-auto h-12 w-12 text-gray-400" />
          <h3 className="mt-2 text-sm font-medium text-gray-900">No providers</h3>
          <p className="mt-1 text-sm text-gray-500">Get started by adding a new provider.</p>
          <div className="mt-6">
            <button
              onClick={() => setShowAddModal(true)}
              className="inline-flex items-center px-4 py-2 border border-transparent shadow-sm text-sm font-medium rounded-lg text-white bg-brand-600 hover:bg-brand-700"
            >
              <Plus className="mr-2 h-5 w-5" />
              Add Provider
            </button>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {providers.map((provider) => (
            <div 
              key={provider.id} 
              className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-200 overflow-hidden border border-gray-100"
            >
              <div className="p-6">
                <div className="flex items-start justify-between">
                  {/* Left: Provider Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center space-x-3 mb-3">
                      <h3 className="text-xl font-bold text-gray-900 truncate">{provider.name}</h3>
                      
                      {/* Priority Badge */}
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-bold bg-gradient-to-r from-brand-500 to-accent-500 text-white shadow-sm">
                        P{provider.priority || 5}
                      </span>
                      
                      {/* Type Badge */}
                      <span className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold bg-ocean-100 text-ocean-800">
                        {provider.provider_type?.toUpperCase() || 'UNKNOWN'}
                      </span>
                      
                      {/* Health Badge */}
                      {provider.last_health_check_status && (
                        <span className={`inline-flex items-center px-2.5 py-1 rounded-full text-xs font-semibold ${
                          provider.last_health_check_status === 'healthy' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {provider.last_health_check_status === 'healthy' ? '✓ Healthy' : '✗ Unhealthy'}
                        </span>
                      )}
                    </div>

                    {/* Stats Row */}
                    <div className="flex items-center space-x-6 text-sm text-gray-600">
                      <div className="flex items-center space-x-1">
                        <Tv className="h-4 w-4 text-brand-600" />
                        <span className="font-medium text-gray-900">{provider.total_channels || 0}</span>
                        <span>channels</span>
                      </div>
                      <div className="flex items-center space-x-1">
                        <Film className="h-4 w-4 text-accent-600" />
                        <span className="font-medium text-gray-900">
                          {(provider.total_vod_movies || 0) + (provider.total_vod_series || 0)}
                        </span>
                        <span>VOD</span>
                      </div>
                      {provider.last_sync_at && (
                        <div className="flex items-center space-x-1">
                          <Clock className="h-4 w-4 text-gray-400" />
                          <span>Synced {formatRelativeTime(provider.last_sync_at)}</span>
                        </div>
                      )}
                      {provider.last_health_check_at && (
                        <div className="flex items-center space-x-1">
                          <Activity className="h-4 w-4 text-gray-400" />
                          <span>Checked {formatRelativeTime(provider.last_health_check_at)}</span>
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Right: Actions */}
                  <div className="flex items-center space-x-2 ml-4">
                    {/* Enable/Disable Toggle */}
                    <button
                      onClick={() => handleToggleEnabled(provider)}
                      className={`p-2 rounded-lg transition-all duration-200 ${
                        provider.enabled
                          ? 'text-green-600 hover:bg-green-50'
                          : 'text-gray-400 hover:bg-gray-50'
                      }`}
                      title={provider.enabled ? 'Enabled - Click to disable' : 'Disabled - Click to enable'}
                    >
                      {provider.enabled ? (
                        <ToggleRight className="h-6 w-6" />
                      ) : (
                        <ToggleLeft className="h-6 w-6" />
                      )}
                    </button>

                    {/* Edit Button */}
                    <button
                      onClick={() => handleEdit(provider)}
                      className="p-2 text-ocean-600 hover:text-ocean-700 hover:bg-ocean-50 rounded-lg transition-colors"
                      title="Edit Provider"
                    >
                      <Edit3 className="h-5 w-5" />
                    </button>

                    {/* Test Button */}
                    <button
                      onClick={() => handleTest(provider.id)}
                      disabled={testingIds.has(provider.id)}
                      className="p-2 text-brand-600 hover:text-brand-700 hover:bg-brand-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Test Connection"
                    >
                      <Activity className={`h-5 w-5 ${testingIds.has(provider.id) ? 'animate-pulse' : ''}`} />
                    </button>

                    {/* Sync Button */}
                    <button
                      onClick={() => handleSync(provider.id)}
                      disabled={syncingIds.has(provider.id)}
                      className="p-2 text-accent-600 hover:text-accent-700 hover:bg-accent-50 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                      title="Sync Provider"
                    >
                      <RefreshCw className={`h-5 w-5 ${syncingIds.has(provider.id) ? 'animate-spin' : ''}`} />
                    </button>

                    {/* Delete Button */}
                    <button
                      onClick={() => handleDelete(provider.id)}
                      className="p-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                      title="Delete Provider"
                    >
                      <Trash2 className="h-5 w-5" />
                    </button>
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      <AddProviderModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={(data) => createMutation.mutate(data)}
      />

      <EditProviderModal
        isOpen={showEditModal}
        onClose={() => {
          setShowEditModal(false)
          setSelectedProvider(null)
        }}
        onSubmit={(data) => updateMutation.mutate({ id: selectedProvider.id, data })}
        provider={selectedProvider}
      />
    </div>
  )
}
