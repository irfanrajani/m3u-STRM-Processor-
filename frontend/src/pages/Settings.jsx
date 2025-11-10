import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import api from '../services/api';

export default function Settings() {
  const [activeCategory, setActiveCategory] = useState('Channel Matching');
  const [localSettings, setLocalSettings] = useState({});
  const [hasChanges, setHasChanges] = useState(false);
  const queryClient = useQueryClient();

  const { data: categories } = useQuery({
    queryKey: ['settings-categories'],
    queryFn: async () => {
      const response = await api.get('/api/settings/categories/list');
      return response.data;
    }
  });

  const { data: settings, isLoading } = useQuery({
    queryKey: ['settings'],
    queryFn: async () => {
      const response = await api.get('/api/settings/');
      return response.data;
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
      await api.post('/api/settings/bulk-update', { settings: payload });
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['settings']);
      setHasChanges(false);
      alert('Settings saved successfully!');
    },
    onError: (error) => {
      alert('Failed to save settings: ' + (error.response?.data?.detail || error.message));
    }
  });

  const resetMutation = useMutation({
    mutationFn: async () => {
      await api.post('/api/settings/reset-defaults');
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['settings']);
      setHasChanges(false);
      alert('Settings reset to defaults!');
    }
  });

  const handleSettingChange = (key, value) => {
    setLocalSettings(prev => ({
      ...prev,
      [key]: {
        ...prev[key],
        value
      }
    }));
    setHasChanges(true);
  };

  const handleSave = () => {
    saveMutation.mutate(localSettings);
  };

  const handleReset = () => {
    if (confirm('Are you sure you want to reset all settings to defaults? This cannot be undone.')) {
      resetMutation.mutate();
    }
  };

  const renderSettingInput = (key, setting) => {
    if (!setting) return null;

    const { value, type, description } = setting;

    switch (type) {
      case 'bool':
        return (
          <div className="flex items-center justify-between p-4 bg-gray-700 rounded-lg">
            <div className="flex-1">
              <label className="block text-sm font-medium text-white mb-1">
                {formatSettingName(key)}
              </label>
              <p className="text-sm text-gray-400">{description}</p>
            </div>
            <label className="relative inline-flex items-center cursor-pointer ml-4">
              <input
                type="checkbox"
                checked={value}
                onChange={(e) => handleSettingChange(key, e.target.checked)}
                className="sr-only peer"
              />
              <div className="w-11 h-6 bg-gray-600 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-800 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
            </label>
          </div>
        );

      case 'int':
        return (
          <div className="p-4 bg-gray-700 rounded-lg">
            <label className="block text-sm font-medium text-white mb-1">
              {formatSettingName(key)}
            </label>
            <p className="text-sm text-gray-400 mb-2">{description}</p>
            <input
              type="number"
              value={value}
              onChange={(e) => handleSettingChange(key, parseInt(e.target.value))}
              className="w-full px-3 py-2 bg-gray-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        );

      case 'string':
        // Check if it's a cron schedule
        if (key.includes('schedule')) {
          return (
            <div className="p-4 bg-gray-700 rounded-lg">
              <label className="block text-sm font-medium text-white mb-1">
                {formatSettingName(key)}
              </label>
              <p className="text-sm text-gray-400 mb-2">{description}</p>
              <input
                type="text"
                value={value}
                onChange={(e) => handleSettingChange(key, e.target.value)}
                className="w-full px-3 py-2 bg-gray-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 font-mono"
                placeholder="0 3 * * *"
              />
              <p className="text-xs text-gray-500 mt-1">
                Cron format: minute hour day month weekday
              </p>
            </div>
          );
        }

        // Check if it's a select field
        if (key === 'playlist_prefer_quality') {
          return (
            <div className="p-4 bg-gray-700 rounded-lg">
              <label className="block text-sm font-medium text-white mb-1">
                {formatSettingName(key)}
              </label>
              <p className="text-sm text-gray-400 mb-2">{description}</p>
              <select
                value={value}
                onChange={(e) => handleSettingChange(key, e.target.value)}
                className="w-full px-3 py-2 bg-gray-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="highest">Highest Available</option>
                <option value="4k">4K</option>
                <option value="1080p">1080p</option>
                <option value="720p">720p</option>
              </select>
            </div>
          );
        }

        if (key === 'log_level') {
          return (
            <div className="p-4 bg-gray-700 rounded-lg">
              <label className="block text-sm font-medium text-white mb-1">
                {formatSettingName(key)}
              </label>
              <p className="text-sm text-gray-400 mb-2">{description}</p>
              <select
                value={value}
                onChange={(e) => handleSettingChange(key, e.target.value)}
                className="w-full px-3 py-2 bg-gray-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="DEBUG">DEBUG</option>
                <option value="INFO">INFO</option>
                <option value="WARNING">WARNING</option>
                <option value="ERROR">ERROR</option>
              </select>
            </div>
          );
        }

        // Default text input
        return (
          <div className="p-4 bg-gray-700 rounded-lg">
            <label className="block text-sm font-medium text-white mb-1">
              {formatSettingName(key)}
            </label>
            <p className="text-sm text-gray-400 mb-2">{description}</p>
            <input
              type="text"
              value={value}
              onChange={(e) => handleSettingChange(key, e.target.value)}
              className="w-full px-3 py-2 bg-gray-600 text-white rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder={key.includes('url') || key.includes('host') ? 'http://...' : ''}
            />
          </div>
        );

      default:
        return null;
    }
  };

  const formatSettingName = (key) => {
    return key
      .split('_')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-gray-400">Loading settings...</div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-white">Settings</h1>
        <div className="flex gap-2">
          {hasChanges && (
            <span className="text-yellow-400 text-sm flex items-center">
              <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
              </svg>
              Unsaved changes
            </span>
          )}
          <button
            onClick={handleReset}
            disabled={resetMutation.isLoading}
            className="px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-500 transition-colors disabled:opacity-50"
          >
            Reset to Defaults
          </button>
          <button
            onClick={handleSave}
            disabled={saveMutation.isLoading || !hasChanges}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors disabled:opacity-50"
          >
            {saveMutation.isLoading ? 'Saving...' : 'Save Changes'}
          </button>
        </div>
      </div>

      <div className="grid grid-cols-4 gap-6">
        {/* Category Sidebar */}
        <div className="col-span-1 space-y-1">
          {categories && Object.keys(categories).map(category => (
            <button
              key={category}
              onClick={() => setActiveCategory(category)}
              className={`w-full text-left px-4 py-2 rounded-md transition-colors ${
                activeCategory === category
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-gray-700'
              }`}
            >
              {category}
            </button>
          ))}
        </div>

        {/* Settings Panel */}
        <div className="col-span-3 space-y-4">
          <h2 className="text-xl font-semibold text-white mb-4">{activeCategory}</h2>

          {categories && categories[activeCategory]?.map(key => (
            <div key={key}>
              {renderSettingInput(key, localSettings[key])}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
