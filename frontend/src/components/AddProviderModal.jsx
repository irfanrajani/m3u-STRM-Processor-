import { useState } from 'react'
import { X, Plus, Trash2 } from 'lucide-react'
import toast from 'react-hot-toast'

export default function AddProviderModal({ isOpen, onClose, onSubmit }) {
  const emptyState = {
    name: '',
    provider_type: 'xstream',
    enabled: true,
    priority: 5,
    health_check_enabled: true,
    health_check_timeout: 10,
    // Xstream
    xstream_host: '',
    xstream_username: '',
    xstream_password: '',
    xstream_backup_hosts: [''],
    // M3U
    m3u_url: '',
    m3u_backup_urls: [''],
    epg_url: '',
  }
  const [formData, setFormData] = useState(emptyState)

  const normalizeUrl = (u) => {
    if (!u) return ''
    let url = u.trim()
    if (!/^https?:\/\//i.test(url)) url = 'http://' + url
    return url.replace(/\/$/, '')
  }

  const sanitizePayload = (data) => {
    const payload = { ...data };
    if (payload.provider_type === 'xstream') {
      delete payload.m3u_url;
      delete payload.m3u_backup_urls;
      payload.xstream_host = normalizeUrl(payload.xstream_host);
      payload.xstream_backup_hosts = (payload.xstream_backup_hosts || [])
        .filter(h => h.trim())
        .map(normalizeUrl);
    } else {
      delete payload.xstream_host;
      delete payload.xstream_username;
      delete payload.xstream_password;
      delete payload.xstream_backup_hosts;
      payload.m3u_url = normalizeUrl(payload.m3u_url);
      payload.m3u_backup_urls = (payload.m3u_backup_urls || [])
        .filter(u => u.trim())
        .map(normalizeUrl);
    }
    return payload;
  };

  const handleSubmit = (e) => {
    e.preventDefault()
    const payload = sanitizePayload()
    if (payload.provider_type === 'xstream' && (!payload.xstream_host || !payload.xstream_username || !payload.xstream_password)) {
      toast.error('Xstream host, username & password required')
      return
    }
    if (payload.provider_type === 'm3u' && !payload.m3u_url) {
      toast.error('M3U playlist URL required')
      return
    }
    onSubmit(payload)
    toast.success('Provider created')
    handleClose()
  }

  const handleClose = () => {
    setFormData(emptyState)
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

          {/* Advanced Common Fields */}
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Priority</label>
              <input
                type="number"
                min={1}
                max={10}
                value={formData.priority}
                onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value||'5',10) })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-brand-500"
              />
            </div>
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Health Check</label>
              <div className="flex items-center space-x-3">
                <label className="flex items-center text-sm">
                  <input
                    type="checkbox"
                    checked={formData.health_check_enabled}
                    onChange={(e)=> setFormData({ ...formData, health_check_enabled: e.target.checked })}
                    className="h-4 w-4 text-brand-600 border-gray-300 rounded"
                  />
                  <span className="ml-2">Enabled</span>
                </label>
                <input
                  type="number"
                  min={5}
                  max={60}
                  value={formData.health_check_timeout}
                  onChange={(e)=> setFormData({ ...formData, health_check_timeout: parseInt(e.target.value||'10',10) })}
                  className="w-20 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                  title="Timeout (seconds)"
                />
              </div>
            </div>
          </div>

          {/* Xstream Fields */}
          {formData.provider_type === 'xstream' && (
            <div className="space-y-4 p-4 bg-gray-50 rounded-md">
              <h3 className="font-medium text-gray-900">Xstream Configuration</h3>

              <div className="grid grid-cols-2 gap-4">
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
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Backup Hosts</label>
                  {formData.xstream_backup_hosts.map((h, idx) => (
                    <div key={idx} className="flex items-center mb-2">
                      <input
                        type="text"
                        value={h}
                        onChange={(e)=> {
                          const arr = [...formData.xstream_backup_hosts];
                          arr[idx] = e.target.value;
                          setFormData({ ...formData, xstream_backup_hosts: arr })
                        }}
                        className="flex-1 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                        placeholder="http://backup-host:8080"
                      />
                      <button type="button" onClick={()=> {
                        const arr = formData.xstream_backup_hosts.filter((_,i)=> i!==idx)
                        setFormData({ ...formData, xstream_backup_hosts: arr.length?arr:[''] })
                      }} className="ml-2 text-danger hover:text-red-700">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  <button type="button" onClick={()=> {
                    setFormData({ ...formData, xstream_backup_hosts: [...formData.xstream_backup_hosts, ''] })
                  }} className="flex items-center space-x-1 text-brand-600 hover:text-brand-700 text-sm">
                    <Plus className="h-4 w-4" /><span>Add Backup</span>
                  </button>
                </div>
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

              <div className="grid grid-cols-2 gap-4">
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
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">Backup URLs</label>
                  {formData.m3u_backup_urls.map((u, idx) => (
                    <div key={idx} className="flex items-center mb-2">
                      <input
                        type="text"
                        value={u}
                        onChange={(e)=> {
                          const arr = [...formData.m3u_backup_urls];
                          arr[idx] = e.target.value;
                          setFormData({ ...formData, m3u_backup_urls: arr })
                        }}
                        className="flex-1 px-2 py-1 border border-gray-300 rounded focus:outline-none focus:ring-2 focus:ring-brand-500 text-sm"
                        placeholder="http://backup-playlist.m3u"
                      />
                      <button type="button" onClick={()=> {
                        const arr = formData.m3u_backup_urls.filter((_,i)=> i!==idx)
                        setFormData({ ...formData, m3u_backup_urls: arr.length?arr:[''] })
                      }} className="ml-2 text-danger hover:text-red-700">
                        <Trash2 className="h-4 w-4" />
                      </button>
                    </div>
                  ))}
                  <button type="button" onClick={()=> {
                    setFormData({ ...formData, m3u_backup_urls: [...formData.m3u_backup_urls, ''] })
                  }} className="flex items-center space-x-1 text-brand-600 hover:text-brand-700 text-sm">
                    <Plus className="h-4 w-4" /><span>Add Backup</span>
                  </button>
                </div>
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
              className="px-5 py-2 rounded-md shadow-glow-brand text-sm font-semibold text-white bg-brand-600 hover:bg-brand-500 transition"
            >
              Add Provider
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
