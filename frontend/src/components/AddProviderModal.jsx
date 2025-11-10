import { useState } from 'react'
import { X } from 'lucide-react'

export default function AddProviderModal({ isOpen, onClose, onSubmit }) {
  const [formData, setFormData] = useState({
    name: '',
    provider_type: 'xstream',
    enabled: true,
    // Xstream fields
    xstream_host: '',
    xstream_username: '',
    xstream_password: '',
    // M3U fields
    m3u_url: '',
    epg_url: '',
  })

  const handleSubmit = (e) => {
    e.preventDefault()
    onSubmit(formData)
    handleClose()
  }

  const handleClose = () => {
    setFormData({
      name: '',
      provider_type: 'xstream',
      enabled: true,
      xstream_host: '',
      xstream_username: '',
      xstream_password: '',
      m3u_url: '',
      epg_url: '',
    })
    onClose()
  }

  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full mx-4 max-h-[90vh] overflow-y-auto">
        <div className="flex items-center justify-between p-6 border-b">
          <h2 className="text-2xl font-bold text-gray-900">Add Provider</h2>
          <button
            onClick={handleClose}
            className="text-gray-400 hover:text-gray-600"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="p-6 space-y-6">
          {/* Basic Info */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Provider Name *
            </label>
            <input
              type="text"
              required
              value={formData.name}
              onChange={(e) => setFormData({ ...formData, name: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="My IPTV Provider"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Provider Type *
            </label>
            <select
              value={formData.provider_type}
              onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <option value="xstream">Xstream API (Xtream Codes)</option>
              <option value="m3u">M3U Playlist</option>
            </select>
          </div>

          {/* Xstream Fields */}
          {formData.provider_type === 'xstream' && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-900">Xstream Configuration</h3>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Host URL *
                </label>
                <input
                  type="url"
                  required
                  value={formData.xstream_host}
                  onChange={(e) => setFormData({ ...formData, xstream_host: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="http://provider.com:8080"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username *
                </label>
                <input
                  type="text"
                  required
                  value={formData.xstream_username}
                  onChange={(e) => setFormData({ ...formData, xstream_username: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password *
                </label>
                <input
                  type="password"
                  required
                  value={formData.xstream_password}
                  onChange={(e) => setFormData({ ...formData, xstream_password: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
              </div>
            </div>
          )}

          {/* M3U Fields */}
          {formData.provider_type === 'm3u' && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-900">M3U Configuration</h3>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  M3U Playlist URL *
                </label>
                <input
                  type="url"
                  required
                  value={formData.m3u_url}
                  onChange={(e) => setFormData({ ...formData, m3u_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="http://provider.com/playlist.m3u"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  EPG URL (Optional)
                </label>
                <input
                  type="url"
                  value={formData.epg_url}
                  onChange={(e) => setFormData({ ...formData, epg_url: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="http://provider.com/epg.xml"
                />
              </div>
            </div>
          )}

          <div className="flex items-center">
            <input
              type="checkbox"
              checked={formData.enabled}
              onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
              className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
            />
            <label className="ml-2 block text-sm text-gray-900">
              Enable provider immediately
            </label>
          </div>

          {/* Actions */}
          <div className="flex justify-end space-x-3 pt-4 border-t">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              className="px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
            >
              Add Provider
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
