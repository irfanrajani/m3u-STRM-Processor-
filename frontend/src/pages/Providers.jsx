import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getProviders, createProvider, deleteProvider, testProvider, syncProvider } from '../services/api'
import { Plus, Trash2, TestTube, RefreshCw } from 'lucide-react'
import AddProviderModal from '../components/AddProviderModal'

export default function Providers() {
  const queryClient = useQueryClient()
  const [showAddModal, setShowAddModal] = useState(false)

  const { data, isLoading } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const createMutation = useMutation({
    mutationFn: createProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
      setShowAddModal(false)
    },
  })

  const deleteMutation = useMutation({
    mutationFn: deleteProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
    },
  })

  const testMutation = useMutation({
    mutationFn: testProvider,
  })

  const syncMutation = useMutation({
    mutationFn: syncProvider,
    onSuccess: () => {
      queryClient.invalidateQueries(['providers'])
    },
  })

  if (isLoading) {
    return <div className="text-center py-10">Loading...</div>
  }

  const providers = data?.data || []

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Providers</h1>
        <button
          onClick={() => setShowAddModal(true)}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Plus className="mr-2 h-4 w-4" />
          Add Provider
        </button>
      </div>

      <div className="bg-white shadow overflow-hidden sm:rounded-md">
        <ul className="divide-y divide-gray-200">
          {providers.map((provider) => (
            <li key={provider.id} className="px-6 py-4">
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <div className="flex items-center">
                    <h3 className="text-lg font-medium text-gray-900">{provider.name}</h3>
                    <span className={`ml-3 px-2 py-1 text-xs rounded-full ${
                      provider.enabled
                        ? 'bg-green-100 text-green-800'
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {provider.enabled ? 'Enabled' : 'Disabled'}
                    </span>
                    <span className="ml-2 px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                      {provider.provider_type.toUpperCase()}
                    </span>
                  </div>
                  <div className="mt-2 text-sm text-gray-500">
                    {provider.total_channels} channels • {provider.total_vod_movies} movies • {provider.total_vod_series} series
                  </div>
                </div>
                <div className="flex space-x-2">
                  <button
                    onClick={() => testMutation.mutate(provider.id)}
                    className="p-2 text-gray-600 hover:text-blue-600"
                    title="Test Connection"
                  >
                    <TestTube className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => syncMutation.mutate(provider.id)}
                    className="p-2 text-gray-600 hover:text-green-600"
                    title="Sync Provider"
                  >
                    <RefreshCw className="h-5 w-5" />
                  </button>
                  <button
                    onClick={() => deleteMutation.mutate(provider.id)}
                    className="p-2 text-gray-600 hover:text-red-600"
                    title="Delete Provider"
                  >
                    <Trash2 className="h-5 w-5" />
                  </button>
                </div>
              </div>
            </li>
          ))}
        </ul>
      </div>

      <AddProviderModal
        isOpen={showAddModal}
        onClose={() => setShowAddModal(false)}
        onSubmit={(data) => createMutation.mutate(data)}
      />
    </div>
  )
}
