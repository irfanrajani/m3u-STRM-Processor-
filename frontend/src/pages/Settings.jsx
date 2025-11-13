import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Settings as SettingsIcon, Save, RefreshCw, AlertCircle, Sliders } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

// Use shared api client (handles auth, errors, proxy) avoiding CORS issues.

export default function Settings() {
  const [localSettings, setLocalSettings] = useState({});
  const [hasChanges, setHasChanges] = useState(false);
  const queryClient = useQueryClient();

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await api.get('/settings/');
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
    mutationFn: async (settingsToSave) => {
      const payload = {};
      Object.keys(settingsToSave).forEach(key => {
        payload[key] = settingsToSave[key].value;
      });
      await api.post('/settings/bulk-update', { settings: payload });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['settings']);
      setHasChanges(false);
      toast.success('Settings saved successfully! Re-sync providers to apply changes.');
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

  const handleSave = () => {
    saveMutation.mutate(localSettings);
  };

  const handleReset = () => {
    setLocalSettings(settings);
    setHasChanges(false);
  };

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
    'Channel Matching': [
      'fuzzy_match_threshold',
      'enable_logo_matching',
      'logo_match_threshold'
    ],
    'Quality Analysis': [
      'enable_bitrate_analysis',
      'ffprobe_timeout'
    ],
    'Health Checks': [
      'health_check_enabled',
      'health_check_timeout',
      'health_check_failure_threshold'
    ]
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
          Configure automatic channel matching and quality analysis
        </p>
      </div>

      {/* Save Bar */}
      {hasChanges && (
        <div className="mb-6 bg-yellow-50 border-l-4 border-yellow-400 p-4 rounded-lg flex items-center justify-between">
          <div className="flex items-center">
            <AlertCircle className="h-5 w-5 text-yellow-600 mr-3" />
            <p className="text-sm text-yellow-700">
              You have unsaved changes. Click Save to apply them.
            </p>
          </div>
          <div className="flex space-x-3">
            <button
              onClick={handleReset}
              className="px-4 py-2 text-sm text-gray-700 bg-white border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              Reset
            </button>
            <button
              onClick={handleSave}
              disabled={saveMutation.isLoading}
              className="px-4 py-2 text-sm text-white bg-brand-600 rounded-lg hover:bg-brand-700 disabled:opacity-50 flex items-center space-x-2"
            >
              {saveMutation.isLoading ? (
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

      {/* Settings Categories */}
      <div className="space-y-6">
        {Object.entries(settingsByCategory).map(([category, keys]) => (
          <div key={category} className="bg-white rounded-lg shadow-md overflow-hidden">
            <div className="bg-gradient-to-r from-brand-50 to-accent-50 px-6 py-4 border-b border-gray-200">
              <h2 className="text-xl font-bold text-gray-900 flex items-center">
                <Sliders className="h-5 w-5 mr-2 text-brand-600" />
                {category}
              </h2>
            </div>
            <div className="p-6 space-y-6">
              {keys.map(key => {
                const setting = localSettings[key];
                if (!setting) return null;

                return (
                  <div key={key} className="flex items-start justify-between py-4 border-b border-gray-100 last:border-0">
                    <div className="flex-1 mr-8">
                      <h3 className="text-sm font-semibold text-gray-900 mb-1">
                        {key.split('_').map(word => word.charAt(0).toUpperCase() + word.slice(1)).join(' ')}
                      </h3>
                      <p className="text-sm text-gray-600">
                        {setting.description}
                      </p>
                    </div>
                    <div className="flex-shrink-0 w-64">
                      {renderSettingInput(key, setting)}
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      {/* Help Text */}
      <div className="mt-8 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
        <div className="flex">
          <AlertCircle className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-700">
            <p className="font-semibold mb-1">Important Notes:</p>
            <ul className="list-disc list-inside space-y-1">
              <li><strong>Fuzzy Match Threshold</strong>: Higher values (85-95) = stricter matching, fewer duplicates merged. Lower values (70-85) = more aggressive matching, more channels combined.</li>
              <li><strong>Logo Matching</strong>: Uses image comparison to verify channels are the same. Recommended to keep enabled.</li>
              <li><strong>Changes apply on next sync</strong>: Re-sync your providers after changing matching settings to reprocess channels.</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
