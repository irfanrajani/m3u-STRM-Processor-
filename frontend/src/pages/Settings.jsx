import { useState } from 'react'
import { Save } from 'lucide-react'

export default function Settings() {
  const [settings, setSettings] = useState({
    fuzzyMatchThreshold: 85,
    healthCheckSchedule: '0 3 * * *',
    healthCheckTimeout: 10,
    maxConcurrentHealthChecks: 50,
    enableBitrateAnalysis: true,
    enableLogoMatching: true,
    logoMatchThreshold: 90,
  })

  const handleSave = () => {
    // Save settings via API
    console.log('Saving settings:', settings)
  }

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
        <button
          onClick={handleSave}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700"
        >
          <Save className="mr-2 h-4 w-4" />
          Save Settings
        </button>
      </div>

      <div className="space-y-6">
        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Channel Matching</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Fuzzy Match Threshold (0-100)
              </label>
              <input
                type="number"
                min="0"
                max="100"
                value={settings.fuzzyMatchThreshold}
                onChange={(e) => setSettings({ ...settings, fuzzyMatchThreshold: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Minimum similarity score for matching channels across providers
              </p>
            </div>

            <div className="flex items-center">
              <input
                type="checkbox"
                checked={settings.enableLogoMatching}
                onChange={(e) => setSettings({ ...settings, enableLogoMatching: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Enable logo-based matching
              </label>
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Health Checks</h2>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">
                Schedule (Cron Format)
              </label>
              <input
                type="text"
                value={settings.healthCheckSchedule}
                onChange={(e) => setSettings({ ...settings, healthCheckSchedule: e.target.value })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
              <p className="mt-1 text-sm text-gray-500">
                Default: 0 3 * * * (Daily at 3 AM)
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Timeout (seconds)
              </label>
              <input
                type="number"
                value={settings.healthCheckTimeout}
                onChange={(e) => setSettings({ ...settings, healthCheckTimeout: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">
                Max Concurrent Checks
              </label>
              <input
                type="number"
                value={settings.maxConcurrentHealthChecks}
                onChange={(e) => setSettings({ ...settings, maxConcurrentHealthChecks: parseInt(e.target.value) })}
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500"
              />
            </div>
          </div>
        </div>

        <div className="bg-white shadow rounded-lg p-6">
          <h2 className="text-lg font-semibold text-gray-900 mb-4">Quality Analysis</h2>
          <div className="space-y-4">
            <div className="flex items-center">
              <input
                type="checkbox"
                checked={settings.enableBitrateAnalysis}
                onChange={(e) => setSettings({ ...settings, enableBitrateAnalysis: e.target.checked })}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <label className="ml-2 block text-sm text-gray-900">
                Enable bitrate analysis with FFprobe
              </label>
            </div>
            <p className="text-sm text-gray-500">
              Uses FFprobe to detect stream quality. Disable for faster processing.
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}
