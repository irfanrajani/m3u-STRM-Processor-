import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, Server, Radio, Film, TrendingUp, AlertCircle } from 'lucide-react';
import axios from 'axios';
import RealTimeMonitor from '../components/RealTimeMonitor';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

function StatCard({ title, value, icon: Icon, color, loading }) {
  return (
    <div className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          {loading ? (
            <div className="mt-2">
              <div className="h-8 w-20 bg-gray-200 rounded animate-pulse"></div>
            </div>
          ) : (
            <p className={`text-3xl font-bold mt-2 ${color}`}>{value}</p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
          <Icon className={`h-8 w-8 ${color}`} />
        </div>
      </div>
    </div>
  );
}

function QuickActionCard({ title, description, icon: Icon, color, onClick, loading }) {
  return (
    <button
      onClick={onClick}
      disabled={loading}
      className={`w-full text-left bg-white rounded-lg shadow-md p-4 hover:shadow-lg transition-all disabled:opacity-50 border-l-4 ${color.replace('text-', 'border-')}`}
    >
      <div className="flex items-start space-x-3">
        <div className={`p-2 rounded-lg ${color.replace('text-', 'bg-').replace('-600', '-100')}`}>
          <Icon className={`h-5 w-5 ${color}`} />
        </div>
        <div>
          <h3 className="font-semibold text-gray-900">{title}</h3>
          <p className="text-sm text-gray-600 mt-1">{description}</p>
        </div>
      </div>
    </button>
  );
}

export default function DashboardEnhanced() {
  const { data: systemStats, isLoading: statsLoading } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      try {
        const response = await axios.get(`${API_URL}/api/system/stats`);
        return response.data;
      } catch (err) {
        console.error('Failed to fetch stats:', err);
        return {
          providers: 0,
          channels: 0,
          vod: 0,
          active_streams: 0
        };
      }
    },
    refetchInterval: 30000 // Refresh every 30 seconds
  });

  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/providers/`);
      return response.data;
    }
  });

  const { data: vodStats } = useQuery({
    queryKey: ['vod-stats'],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/vod/stats`);
      return response.data;
    }
  });

  const syncProvider = async (providerId) => {
    try {
      await axios.post(`${API_URL}/api/providers/${providerId}/sync`);
    } catch (err) {
      console.error('Failed to sync provider:', err);
    }
  };

  const generateVODStrms = async () => {
    try {
      await axios.post(`${API_URL}/api/vod/generate-strm`);
    } catch (err) {
      console.error('Failed to generate STRM files:', err);
    }
  };

  const runHealthCheck = async () => {
    try {
      await axios.post(`${API_URL}/api/health/check-all`);
    } catch (err) {
      console.error('Failed to run health check:', err);
    }
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent mb-2">
          Dashboard
        </h1>
        <p className="text-gray-600">
          Monitor your IPTV stream manager in real-time
        </p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          title="Providers"
          value={systemStats?.providers || 0}
          icon={Server}
          color="text-blue-600"
          loading={statsLoading}
        />
        <StatCard
          title="Channels"
          value={systemStats?.channels || 0}
          icon={Radio}
          color="text-green-600"
          loading={statsLoading}
        />
        <StatCard
          title="VOD Items"
          value={(vodStats?.total_movies || 0) + (vodStats?.total_series || 0)}
          icon={Film}
          color="text-purple-600"
          loading={statsLoading}
        />
        <StatCard
          title="Active Streams"
          value={systemStats?.active_streams || 0}
          icon={Activity}
          color="text-orange-600"
          loading={statsLoading}
        />
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
        {/* Real-Time Monitor - Takes 2 columns on xl screens */}
        <div className="xl:col-span-2">
          <RealTimeMonitor />
        </div>

        {/* Quick Actions Sidebar */}
        <div className="space-y-6">
          {/* Provider Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <Server className="h-5 w-5 mr-2 text-brand-600" />
              Provider Actions
            </h2>
            <div className="space-y-3">
              {providers && providers.length > 0 ? (
                providers.slice(0, 3).map(provider => (
                  <button
                    key={provider.id}
                    onClick={() => syncProvider(provider.id)}
                    className="w-full text-left px-4 py-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors"
                  >
                    <div className="font-medium text-gray-900">{provider.name}</div>
                    <div className="text-xs text-gray-600 mt-1">
                      {provider.total_channels || 0} channels
                    </div>
                  </button>
                ))
              ) : (
                <div className="text-sm text-gray-600 text-center py-4">
                  No providers configured
                </div>
              )}
            </div>
          </div>

          {/* Quick Actions */}
          <div className="bg-white rounded-xl shadow-lg p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
              <TrendingUp className="h-5 w-5 mr-2 text-brand-600" />
              Quick Actions
            </h2>
            <div className="space-y-3">
              <QuickActionCard
                title="Generate STRM Files"
                description="Create STRM files for all VOD content"
                icon={Film}
                color="text-purple-600"
                onClick={generateVODStrms}
              />
              <QuickActionCard
                title="Run Health Check"
                description="Check all streams for availability"
                icon={Activity}
                color="text-green-600"
                onClick={runHealthCheck}
              />
            </div>
          </div>

          {/* VOD Statistics */}
          {vodStats && (
            <div className="bg-white rounded-xl shadow-lg p-6">
              <h2 className="text-lg font-bold text-gray-900 mb-4 flex items-center">
                <Film className="h-5 w-5 mr-2 text-purple-600" />
                VOD Library
              </h2>
              <div className="space-y-3">
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Movies</span>
                  <span className="font-semibold text-purple-600">{vodStats.total_movies || 0}</span>
                </div>
                <div className="flex items-center justify-between py-2 border-b border-gray-100">
                  <span className="text-sm text-gray-600">Series</span>
                  <span className="font-semibold text-purple-600">{vodStats.total_series || 0}</span>
                </div>
                <div className="flex items-center justify-between py-2">
                  <span className="text-sm text-gray-600">Episodes</span>
                  <span className="font-semibold text-purple-600">{vodStats.total_episodes || 0}</span>
                </div>
              </div>
            </div>
          )}

          {/* System Health */}
          <div className="bg-gradient-to-br from-green-50 to-green-100 rounded-xl shadow-lg p-6 border border-green-200">
            <div className="flex items-start space-x-3">
              <div className="p-2 bg-green-500 rounded-lg">
                <AlertCircle className="h-5 w-5 text-white" />
              </div>
              <div>
                <h3 className="font-semibold text-green-900">System Operational</h3>
                <p className="text-sm text-green-700 mt-1">
                  All services are running normally. Real-time monitoring is active.
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Info Banner */}
      <div className="mt-8 bg-blue-50 border-l-4 border-blue-400 p-4 rounded-lg">
        <div className="flex items-start">
          <AlertCircle className="h-5 w-5 text-blue-600 mr-3 flex-shrink-0 mt-0.5" />
          <div className="text-sm text-blue-700">
            <p className="font-semibold mb-1">Dashboard Features:</p>
            <ul className="list-disc list-inside space-y-1">
              <li>Real-time WebSocket connection for instant updates</li>
              <li>Live health check results and stream failover notifications</li>
              <li>Provider sync progress tracking</li>
              <li>Statistics updated every 30 seconds</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}
