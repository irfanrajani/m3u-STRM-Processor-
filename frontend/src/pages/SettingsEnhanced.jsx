import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Settings as SettingsIcon, Save, RefreshCw, AlertCircle, Sliders,
  Film, Bell, Gauge, Radio, Zap, Shield
} from 'lucide-react';
import axios from 'axios';
import toast from 'react-hot-toast';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function SettingsEnhanced() {
  const [localSettings, setLocalSettings] = useState({});
  const [notificationConfig, setNotificationConfig] = useState({
    telegram: { enabled: false, bot_token: '', chat_id: '', min_level: 'INFO' },
    pushover: { enabled: false, user_key: '', api_token: '', min_level: 'INFO' },
    webhook: { enabled: false, url: '', min_level: 'INFO' }
  });
  const [bandwidthConfig, setBandwidthConfig] = useState({
    global_limit_mbps: null,
    enabled: false
  });
  const [hasChanges, setHasChanges] = useState(false);
  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/settings/`);
      const settingsMap = {};
      response.data.forEach(setting => {
        settingsMap[setting.key] = setting;
      });
      return settingsMap;
    },
    onSuccess: (data) => {
      setLocalSettings(data);
    }
  });

  const saveMutation = useMutation({
    mutationFn: async (data) => {
      const payload = {};
      Object.keys(data.settings).forEach(key => {
        payload[key] = data.settings[key].value;
      });

      await axios.post(`${API_URL}/api/settings/bulk-update`, { settings: payload });

      // TODO: Save notification and bandwidth config to backend
      // These would require new API endpoints
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['settings']);
      setHasChanges(false);
      toast.success('Settings saved successfully!');
    },
    onError: (error) => {
      toast.error('Failed to save settings');
    }
  });

  const handleChange = (key, value) => {
    setLocalSettings(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        value: value
      }
    }));
    setHasChanges(true);
  };

  const handleNotificationChange = (provider, field, value) => {
    setNotificationConfig(prev => ({
      ...prev,
      [provider]: {
        ...prev[provider],
        [field]: value
      }
    }));
    setHasChanges(true);
  };

  const handleBandwidthChange = (field, value) => {
    setBandwidthConfig(prev => ({
      ...prev,
      [field]: value
    }));
    setHasChanges(true);
  };

  const handleSave = () => {
    saveMutation.mutate({
      settings: localSettings,
      notifications: notificationConfig,
      bandwidth: bandwidthConfig
    });
  };

  const handleReset = () => {
    setLocalSettings(settings);
    setHasChanges(false);
  });

  const generateVODStrms = useMutation({
    mutationFn: async () => {
      await axios.post(`${API_URL}/api/vod/generate-strm`);
    },
    onSuccess: () => {
      toast.success('VOD STRM generation started! Check the dashboard for progress.');
    },
    onError: () => {
      toast.error('Failed to start VOD generation');
    }
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Loading settings...</p>
        </div>
      </div>
    );
  }

  const settingsByCategory = {
    'Channel Matching': {
      icon: Radio,
      color: 'from-blue-500 to-blue-600',
      settings: [
        'fuzzy_match_threshold',
        'enable_logo_matching',
        'logo_match_threshold'
      ]
    },
    'Quality Analysis': {
      icon: Gauge,
      color: 'from-green-500 to-green-600',
      settings: [
        'enable_bitrate_analysis',
        'ffprobe_timeout'
      ]
    },
    'Health Checks': {
      icon: Shield,
      color: 'from-red-500 to-red-600',
      settings: [
        'health_check_enabled',
        'health_check_timeout',
        'health_check_failure_threshold'
      ]
    }
  };

  const renderSettingInput = (key, setting) => {
    if (!setting) return null;

    const value = setting.value;
    const type = setting.value_type;

    if (type === 'bool' || type === 'boolean') {
      return (
        <label className="relative inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={value}
            onChange={(e) => handleChange(key, e.target.checked)}
            className="sr-only peer"
          />
          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-brand-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-brand-600"></div>
        </label>
      );
    }

    if (type === 'int' || type === 'integer') {
      return (
        <div className="flex items-center space-x-4">
          <input
            type="range"
            min="0"
            max="100"
            value={value}
            onChange={(e) => handleChange(key, parseInt(e.target.value))}
            className="flex-1 h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
          />
          <span className="w-12 text-center font-semibold text-brand-600">{value}</span>
        </div>
      );
    }

    return (
      <input
        type="text"
        value={value || ''}
        onChange={(e) => handleChange(key, e.target.value)}
        className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
      />
    );
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent mb-2">
          System Settings
        </h1>
        <p className="text-gray-600">
          Configure channel matching, VOD processing, notifications, and performance
        </p>
      </div>

      {/* Save Bar */}
      {hasChanges && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg flex items-center justify-between sticky top-0 z-10 shadow-md">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-3" />
            <p className="text-sm text-yellow-700 font-medium">
              You have unsaved changes. Click Save to apply them.
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition"
            >
              Reset
            </button>
            <button
              onClick={handleSave}
              disabled={saveMutation.isPending}
              className="px-4 py-2 text-sm text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50 flex items-center space-x-2 transition"
            >
              {saveMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Saving...</span>
                </>
              ) : (
                <>
                  <Save className="h-4 w-4" />
                  <span>Save Changes</span>
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Settings Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-6 mb-6">
        {/* Core Settings */}
        {Object.entries(settingsByCategory).map(([category, config]) => {
          const Icon = config.icon;
          return (
            <div key={category} className="bg-white rounded-xl shadow-lg overflow-hidden hover:shadow-xl transition-shadow">
              <div className={`bg-gradient-to-r ${config.color} px-6 py-4`}>
                <h2 className="text-xl font-bold text-white flex items-center">
                  <Icon className="h-5 w-5 mr-2" />
                  {category}
                </h2>
              </div>
              <div className="p-6 space-y-4">
                {config.settings.map(key => {
                  const setting = localSettings[key];
                  if (!setting) return null;

                  return (
                    <div key={key} className="pb-4 border-b border-gray-100 last:border-0">
                      <div className="flex items-start justify-between mb-2">
                        <div className="flex-1 mr-4">
                          <h3 className="text-sm font-semibold text-gray-900">
                            {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                          </h3>
                          <p className="text-xs text-gray-600 mt-1">
                            {setting.description}
                          </p>
                        </div>
                        <div className="flex-shrink-0">
                          {renderSettingInput(key, setting)}
                        </div>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      {/* VOD Processing Section */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-6 hover:shadow-xl transition-shadow">
        <div className="bg-gradient-to-r from-purple-500 to-purple-600 px-6 py-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Film className="h-5 w-5 mr-2" />
            VOD Processing
          </h2>
        </div>
        <div className="p-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between p-4 bg-purple-50 rounded-lg">
              <div>
                <h3 className="font-semibold text-gray-900">STRM File Organization</h3>
                <p className="text-sm text-gray-600 mt-1">
                  Files organized as: Movies/Genre/Title (Year)/ and TV Shows/Genre/Series (Year)/Season XX/
                </p>
              </div>
              <button
                onClick={() => generateVODStrms.mutate()}
                disabled={generateVODStrms.isPending}
                className="px-4 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700 disabled:opacity-50 flex items-center space-x-2 transition"
              >
                {generateVODStrms.isPending ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                    <span>Generating...</span>
                  </>
                ) : (
                  <>
                    <Zap className="h-4 w-4" />
                    <span>Generate STRM Files</span>
                  </>
                )}
              </button>
            </div>
            <div className="text-sm text-gray-600 bg-blue-50 p-4 rounded-lg">
              <p className="font-semibold text-blue-900 mb-2">About STRM Files:</p>
              <ul className="list-disc list-inside space-y-1 text-blue-800">
                <li>STRM files are text files containing stream URLs</li>
                <li>Compatible with Emby, Plex, and Jellyfin</li>
                <li>Automatically organized by genre for easy library management</li>
                <li>Regenerate after adding new VOD content</li>
              </ul>
            </div>
          </div>
        </div>
      </div>

      {/* Notifications Section */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-6 hover:shadow-xl transition-shadow">
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 px-6 py-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Bell className="h-5 w-5 mr-2" />
            Notifications
          </h2>
        </div>
        <div className="p-6 space-y-6">
          {/* Telegram */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Telegram</h3>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationConfig.telegram.enabled}
                  onChange={(e) => handleNotificationChange('telegram', 'enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
              </label>
            </div>
            {notificationConfig.telegram.enabled && (
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="Bot Token"
                  value={notificationConfig.telegram.bot_token}
                  onChange={(e) => handleNotificationChange('telegram', 'bot_token', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                />
                <input
                  type="text"
                  placeholder="Chat ID"
                  value={notificationConfig.telegram.chat_id}
                  onChange={(e) => handleNotificationChange('telegram', 'chat_id', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                />
                <select
                  value={notificationConfig.telegram.min_level}
                  onChange={(e) => handleNotificationChange('telegram', 'min_level', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="INFO">All Messages (INFO)</option>
                  <option value="WARNING">Warnings & Errors</option>
                  <option value="ERROR">Errors Only</option>
                  <option value="CRITICAL">Critical Only</option>
                </select>
              </div>
            )}
          </div>

          {/* Pushover */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Pushover</h3>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationConfig.pushover.enabled}
                  onChange={(e) => handleNotificationChange('pushover', 'enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
              </label>
            </div>
            {notificationConfig.pushover.enabled && (
              <div className="space-y-3">
                <input
                  type="text"
                  placeholder="User Key"
                  value={notificationConfig.pushover.user_key}
                  onChange={(e) => handleNotificationChange('pushover', 'user_key', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                />
                <input
                  type="text"
                  placeholder="API Token"
                  value={notificationConfig.pushover.api_token}
                  onChange={(e) => handleNotificationChange('pushover', 'api_token', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                />
                <select
                  value={notificationConfig.pushover.min_level}
                  onChange={(e) => handleNotificationChange('pushover', 'min_level', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="INFO">All Messages (INFO)</option>
                  <option value="WARNING">Warnings & Errors</option>
                  <option value="ERROR">Errors Only</option>
                  <option value="CRITICAL">Critical Only</option>
                </select>
              </div>
            )}
          </div>

          {/* Webhook */}
          <div className="border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className="font-semibold text-gray-900">Webhook</h3>
              <label className="relative inline-flex items-center cursor-pointer">
                <input
                  type="checkbox"
                  checked={notificationConfig.webhook.enabled}
                  onChange={(e) => handleNotificationChange('webhook', 'enabled', e.target.checked)}
                  className="sr-only peer"
                />
                <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-orange-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-orange-600"></div>
              </label>
            </div>
            {notificationConfig.webhook.enabled && (
              <div className="space-y-3">
                <input
                  type="url"
                  placeholder="Webhook URL"
                  value={notificationConfig.webhook.url}
                  onChange={(e) => handleNotificationChange('webhook', 'url', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                />
                <select
                  value={notificationConfig.webhook.min_level}
                  onChange={(e) => handleNotificationChange('webhook', 'min_level', e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500"
                >
                  <option value="INFO">All Messages (INFO)</option>
                  <option value="WARNING">Warnings & Errors</option>
                  <option value="ERROR">Errors Only</option>
                  <option value="CRITICAL">Critical Only</option>
                </select>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Bandwidth Throttling Section */}
      <div className="bg-white rounded-xl shadow-lg overflow-hidden mb-6 hover:shadow-xl transition-shadow">
        <div className="bg-gradient-to-r from-teal-500 to-teal-600 px-6 py-4">
          <h2 className="text-xl font-bold text-white flex items-center">
            <Gauge className="h-5 w-5 mr-2" />
            Bandwidth Throttling
          </h2>
        </div>
        <div className="p-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="font-semibold text-gray-900">Enable Global Bandwidth Limit</h3>
              <p className="text-sm text-gray-600">Limit total bandwidth usage across all streams</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer">
              <input
                type="checkbox"
                checked={bandwidthConfig.enabled}
                onChange={(e) => handleBandwidthChange('enabled', e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-teal-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-teal-600"></div>
            </label>
          </div>
          {bandwidthConfig.enabled && (
            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Global Limit (Mbps)
              </label>
              <input
                type="number"
                min="1"
                max="1000"
                value={bandwidthConfig.global_limit_mbps || ''}
                onChange={(e) => handleBandwidthChange('global_limit_mbps', parseFloat(e.target.value))}
                placeholder="e.g., 100"
                className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500"
              />
              <p className="text-xs text-gray-500 mt-2">
                Recommended: 50-500 Mbps depending on your connection. Leave empty for unlimited.
              </p>
            </div>
          )}
        </div>
      </div>

      {/* Help Section */}
      <div className="bg-blue-50 border-l-4 border-blue-400 p-6 rounded-lg">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-700">
            <p className="font-semibold mb-2">Important Notes:</p>
            <ul className="list-disc list-inside space-y-1.5">
              <li><strong>Channel Matching</strong>: Changes apply on next provider sync. Higher fuzzy threshold = stricter matching.</li>
              <li><strong>VOD Processing</strong>: STRM files are automatically organized by genre for Emby/Plex/Jellyfin.</li>
              <li><strong>Notifications</strong>: Configure multiple channels for redundancy. Test after saving.</li>
              <li><strong>Bandwidth</strong>: Token bucket algorithm ensures smooth throttling without dropped frames.</li>
              <li><strong>Grace Period</strong>: 300ms wait prevents false failovers during brief provider hiccups.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
