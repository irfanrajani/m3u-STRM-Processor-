import { useState, useEffect } from 'react';
import { X, Plus, Trash2 } from 'lucide-react';
import toast from 'react-hot-toast';

export default function EditProviderModal({ isOpen, onClose, onSubmit, provider }) {
  const [formData, setFormData] = useState({
    name: '',
    provider_type: 'xstream',
    xstream_host: '',
    xstream_username: '',
    xstream_password: '',
    m3u_url: '',
    enabled: true,
    priority: 5,
    health_check_enabled: true,
    health_check_timeout: 10,
    xstream_backup_hosts: [],
    m3u_backup_urls: []
  });

  // Prefill form when provider changes
  useEffect(() => {
    if (provider) {
      setFormData({
        name: provider.name || '',
        provider_type: provider.provider_type || 'xstream',
        xstream_host: provider.xstream_host || '',
        xstream_username: provider.xstream_username || '',
        xstream_password: provider.xstream_password || '',
        m3u_url: provider.m3u_url || '',
        enabled: provider.enabled ?? true,
        priority: provider.priority || 5,
        health_check_enabled: provider.health_check_enabled ?? true,
        health_check_timeout: provider.health_check_timeout || 10,
        xstream_backup_hosts: provider.xstream_backup_hosts || [],
        m3u_backup_urls: provider.m3u_backup_urls || []
      });
    }
  }, [provider]);

  const normalizeUrl = (url) => {
    if (!url) return '';
    let normalized = url.trim();
    if (!/^https?:\/\//i.test(normalized)) {
      normalized = 'http://' + normalized;
    }
    normalized = normalized.replace(/\/+$/, '');
    return normalized;
  };

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
    e.preventDefault();
    
    // Validation
    if (!formData.name.trim()) {
      toast.error('Provider name is required');
      return;
    }

    if (formData.provider_type === 'xstream') {
      if (!formData.xstream_host.trim()) {
        toast.error('XStream Host is required for XStream providers');
        return;
      }
      if (!formData.xstream_username.trim() || !formData.xstream_password.trim()) {
        toast.error('Username and password are required for XStream providers');
        return;
      }
    } else {
      if (!formData.m3u_url.trim()) {
        toast.error('M3U URL is required for M3U providers');
        return;
      }
    }

    const sanitized = sanitizePayload(formData);
    onSubmit(sanitized);
  };

  const addBackupHost = () => {
    setFormData(prev => ({
      ...prev,
      xstream_backup_hosts: [...(prev.xstream_backup_hosts || []), '']
    }));
  };

  const removeBackupHost = (index) => {
    setFormData(prev => ({
      ...prev,
      xstream_backup_hosts: prev.xstream_backup_hosts.filter((_, i) => i !== index)
    }));
  };

  const updateBackupHost = (index, value) => {
    setFormData(prev => ({
      ...prev,
      xstream_backup_hosts: prev.xstream_backup_hosts.map((host, i) => 
        i === index ? value : host
      )
    }));
  };

  const addBackupUrl = () => {
    setFormData(prev => ({
      ...prev,
      m3u_backup_urls: [...(prev.m3u_backup_urls || []), '']
    }));
  };

  const removeBackupUrl = (index) => {
    setFormData(prev => ({
      ...prev,
      m3u_backup_urls: prev.m3u_backup_urls.filter((_, i) => i !== index)
    }));
  };

  const updateBackupUrl = (index, value) => {
    setFormData(prev => ({
      ...prev,
      m3u_backup_urls: prev.m3u_backup_urls.map((url, i) => 
        i === index ? value : url
      )
    }));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <div className="flex items-end justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" aria-hidden="true" onClick={onClose}></div>
        <span className="hidden sm:inline-block sm:align-middle sm:h-screen" aria-hidden="true">&#8203;</span>
        
        <div className="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-2xl sm:w-full">
          <form onSubmit={handleSubmit}>
            <div className="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-2xl font-bold text-gray-900" id="modal-title">Edit Provider</h3>
                <button type="button" onClick={onClose} className="text-gray-400 hover:text-gray-500">
                  <X className="h-6 w-6" />
                </button>
              </div>

              <div className="space-y-4">
                {/* Name */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Provider Name *</label>
                  <input
                    type="text"
                    required
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                    placeholder="My Provider"
                  />
                </div>

                {/* Provider Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">Provider Type</label>
                  <select
                    value={formData.provider_type}
                    onChange={(e) => setFormData({ ...formData, provider_type: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  >
                    <option value="xstream">XStream Codes</option>
                    <option value="m3u">M3U Playlist</option>
                  </select>
                </div>

                {/* Priority */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Priority (1-10) - Higher = preferred
                  </label>
                  <input
                    type="number"
                    min="1"
                    max="10"
                    value={formData.priority}
                    onChange={(e) => setFormData({ ...formData, priority: parseInt(e.target.value) || 5 })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                  />
                </div>

                {/* Health Check */}
                <div className="flex items-center space-x-4">
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.health_check_enabled}
                      onChange={(e) => setFormData({ ...formData, health_check_enabled: e.target.checked })}
                      className="w-4 h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Enable Health Checks</span>
                  </label>
                  
                  {formData.health_check_enabled && (
                    <div className="flex items-center space-x-2">
                      <label className="text-sm text-gray-600">Timeout (seconds):</label>
                      <input
                        type="number"
                        min="5"
                        max="60"
                        value={formData.health_check_timeout}
                        onChange={(e) => setFormData({ ...formData, health_check_timeout: parseInt(e.target.value) || 10 })}
                        className="w-20 px-2 py-1 border border-gray-300 rounded focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                      />
                    </div>
                  )}
                </div>

                {/* Enabled Toggle */}
                <div>
                  <label className="flex items-center space-x-2 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={formData.enabled}
                      onChange={(e) => setFormData({ ...formData, enabled: e.target.checked })}
                      className="w-4 h-4 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
                    />
                    <span className="text-sm font-medium text-gray-700">Enable this provider</span>
                  </label>
                </div>

                {/* XStream Fields */}
                {formData.provider_type === 'xstream' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">XStream Host URL *</label>
                      <input
                        type="text"
                        required
                        value={formData.xstream_host}
                        onChange={(e) => setFormData({ ...formData, xstream_host: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        placeholder="http://example.com:8080"
                      />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Username *</label>
                        <input
                          type="text"
                          required
                          value={formData.xstream_username}
                          onChange={(e) => setFormData({ ...formData, xstream_username: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        />
                      </div>
                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-1">Password *</label>
                        <input
                          type="password"
                          required
                          value={formData.xstream_password}
                          onChange={(e) => setFormData({ ...formData, xstream_password: e.target.value })}
                          className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        />
                      </div>
                    </div>

                    {/* Backup Hosts */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium text-gray-700">Backup Hosts (optional)</label>
                        <button
                          type="button"
                          onClick={addBackupHost}
                          className="inline-flex items-center px-2 py-1 text-xs font-medium text-brand-700 bg-brand-50 rounded hover:bg-brand-100 transition-colors"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Backup
                        </button>
                      </div>
                      <div className="space-y-2">
                        {(formData.xstream_backup_hosts || []).map((host, index) => (
                          <div key={index} className="flex space-x-2">
                            <input
                              type="text"
                              value={host}
                              onChange={(e) => updateBackupHost(index, e.target.value)}
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                              placeholder="http://backup.example.com:8080"
                            />
                            <button
                              type="button"
                              onClick={() => removeBackupHost(index)}
                              className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}

                {/* M3U Fields */}
                {formData.provider_type === 'm3u' && (
                  <>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">M3U URL *</label>
                      <input
                        type="text"
                        required
                        value={formData.m3u_url}
                        onChange={(e) => setFormData({ ...formData, m3u_url: e.target.value })}
                        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                        placeholder="http://example.com/playlist.m3u"
                      />
                    </div>

                    {/* Backup URLs */}
                    <div>
                      <div className="flex justify-between items-center mb-2">
                        <label className="block text-sm font-medium text-gray-700">Backup M3U URLs (optional)</label>
                        <button
                          type="button"
                          onClick={addBackupUrl}
                          className="inline-flex items-center px-2 py-1 text-xs font-medium text-brand-700 bg-brand-50 rounded hover:bg-brand-100 transition-colors"
                        >
                          <Plus className="h-3 w-3 mr-1" />
                          Add Backup
                        </button>
                      </div>
                      <div className="space-y-2">
                        {(formData.m3u_backup_urls || []).map((url, index) => (
                          <div key={index} className="flex space-x-2">
                            <input
                              type="text"
                              value={url}
                              onChange={(e) => updateBackupUrl(index, e.target.value)}
                              className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
                              placeholder="http://backup.example.com/playlist.m3u"
                            />
                            <button
                              type="button"
                              onClick={() => removeBackupUrl(index)}
                              className="px-3 py-2 text-red-600 hover:text-red-700 hover:bg-red-50 rounded-lg transition-colors"
                            >
                              <Trash2 className="h-4 w-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                    </div>
                  </>
                )}
              </div>
            </div>

            <div className="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse space-x-reverse space-x-3">
              <button
                type="submit"
                className="w-full inline-flex justify-center rounded-lg border border-transparent shadow-sm px-4 py-2 bg-brand-600 text-base font-medium text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 sm:ml-3 sm:w-auto sm:text-sm transition-colors shadow-glow-brand"
              >
                Save Changes
              </button>
              <button
                type="button"
                onClick={onClose}
                className="mt-3 w-full inline-flex justify-center rounded-lg border border-gray-300 shadow-sm px-4 py-2 bg-white text-base font-medium text-gray-700 hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-brand-500 sm:mt-0 sm:w-auto sm:text-sm"
              >
                Cancel
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
