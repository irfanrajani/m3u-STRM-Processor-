import { useQuery } from '@tanstack/react-query'
import { Copy, Check, Server, Database, Activity, Link as LinkIcon } from 'lucide-react'
import { useState } from 'react'
import api from '../services/api'

export default function SystemInfo() {
  const [copiedField, setCopiedField] = useState(null)

  const { data: systemInfo, isLoading } = useQuery({
    queryKey: ['systemInfo'],
    queryFn: async () => {
      const response = await api.get('/system/info')
      return response.data
    }
  })

  const { data: health } = useQuery({
    queryKey: ['systemHealth'],
    queryFn: async () => {
      const response = await api.get('/system/health')
      return response.data
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  })

  const copyToClipboard = (text, field) => {
    navigator.clipboard.writeText(text)
    setCopiedField(field)
    setTimeout(() => setCopiedField(null), 2000)
  }

  const CopyButton = ({ text, field }) => (
    <button
      onClick={() => copyToClipboard(text, field)}
      className="ml-2 p-1 text-gray-400 hover:text-blue-600 transition-colors"
      title="Copy to clipboard"
    >
      {copiedField === field ? (
        <Check className="h-4 w-4 text-green-600" />
      ) : (
        <Copy className="h-4 w-4" />
      )}
    </button>
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading system information...</div>
      </div>
    )
  }

  return (
    <div className="px-4 sm:px-0 space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-gray-900">System Information</h1>
        {health && (
          <div className={`px-3 py-1 rounded-full text-sm font-medium ${
            health.status === 'healthy'
              ? 'bg-green-100 text-green-800'
              : 'bg-yellow-100 text-yellow-800'
          }`}>
            {health.status === 'healthy' ? '● Healthy' : '● Degraded'}
          </div>
        )}
      </div>

      {/* Important URLs Section */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <LinkIcon className="h-5 w-5 text-blue-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Important URLs</h2>
        </div>

        <div className="space-y-3">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              HDHomeRun URL (for Emby/Plex)
            </label>
            <div className="flex items-center bg-gray-50 p-3 rounded-md font-mono text-sm">
              <span className="flex-1">{systemInfo?.urls?.hdhr_discover?.replace('/discover.json', '')}</span>
              <CopyButton
                text={systemInfo?.urls?.hdhr_discover?.replace('/discover.json', '')}
                field="hdhr_url"
              />
            </div>
            <p className="text-xs text-gray-500 mt-1">
              Add this URL in Emby: Settings → Live TV → Tuner Devices → Add → HDHomeRun
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Discovery Endpoint
            </label>
            <div className="flex items-center bg-gray-50 p-3 rounded-md font-mono text-sm">
              <span className="flex-1">{systemInfo?.urls?.hdhr_discover}</span>
              <CopyButton text={systemInfo?.urls?.hdhr_discover} field="discover" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Channel Lineup
            </label>
            <div className="flex items-center bg-gray-50 p-3 rounded-md font-mono text-sm">
              <span className="flex-1">{systemInfo?.urls?.hdhr_lineup}</span>
              <CopyButton text={systemInfo?.urls?.hdhr_lineup} field="lineup" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              M3U Playlist
            </label>
            <div className="flex items-center bg-gray-50 p-3 rounded-md font-mono text-sm">
              <span className="flex-1">{systemInfo?.urls?.m3u_playlist}</span>
              <CopyButton text={systemInfo?.urls?.m3u_playlist} field="m3u" />
            </div>
          </div>
        </div>
      </div>

      {/* HDHomeRun Configuration */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Server className="h-5 w-5 text-purple-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">HDHomeRun Emulation</h2>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Device ID</label>
            <div className="bg-gray-50 p-3 rounded-md font-mono text-sm">
              {systemInfo?.hdhr?.device_id}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Tuner Count</label>
            <div className="bg-gray-50 p-3 rounded-md font-mono text-sm">
              {systemInfo?.hdhr?.tuner_count}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Proxy Mode</label>
            <div className="bg-gray-50 p-3 rounded-md font-mono text-sm">
              {systemInfo?.hdhr?.proxy_mode}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Status</label>
            <div className="bg-green-50 p-3 rounded-md text-sm text-green-800 font-medium">
              Enabled
            </div>
          </div>
        </div>
      </div>

      {/* Statistics */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Database className="h-5 w-5 text-green-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">Database Statistics</h2>
        </div>

        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          <div className="text-center">
            <div className="text-3xl font-bold text-blue-600">{systemInfo?.stats?.providers}</div>
            <div className="text-sm text-gray-500 mt-1">Providers</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-green-600">{systemInfo?.stats?.channels}</div>
            <div className="text-sm text-gray-500 mt-1">Channels</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-purple-600">{systemInfo?.stats?.streams}</div>
            <div className="text-sm text-gray-500 mt-1">Streams</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-orange-600">{systemInfo?.stats?.movies}</div>
            <div className="text-sm text-gray-500 mt-1">Movies</div>
          </div>
          <div className="text-center">
            <div className="text-3xl font-bold text-pink-600">{systemInfo?.stats?.series}</div>
            <div className="text-sm text-gray-500 mt-1">Series</div>
          </div>
        </div>
      </div>

      {/* System Details */}
      <div className="bg-white shadow rounded-lg p-6">
        <div className="flex items-center mb-4">
          <Activity className="h-5 w-5 text-gray-600 mr-2" />
          <h2 className="text-xl font-semibold text-gray-900">System Details</h2>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Application</label>
            <div className="text-gray-900">{systemInfo?.app?.name} v{systemInfo?.app?.version}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Platform</label>
            <div className="text-gray-900">{systemInfo?.platform?.os}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Python Version</label>
            <div className="text-gray-900">{systemInfo?.platform?.python_version}</div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Database</label>
            <div className="text-gray-900">{health?.database}</div>
          </div>
        </div>
      </div>

      {/* Output Paths */}
      <div className="bg-white shadow rounded-lg p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Output Paths</h2>

        <div className="space-y-2">
          <div>
            <label className="block text-sm font-medium text-gray-700">STRM Files</label>
            <div className="bg-gray-50 p-2 rounded-md font-mono text-sm text-gray-900">
              {systemInfo?.paths?.strm_output}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Playlists</label>
            <div className="bg-gray-50 p-2 rounded-md font-mono text-sm text-gray-900">
              {systemInfo?.paths?.playlists}
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">EPG Data</label>
            <div className="bg-gray-50 p-2 rounded-md font-mono text-sm text-gray-900">
              {systemInfo?.paths?.epg}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
