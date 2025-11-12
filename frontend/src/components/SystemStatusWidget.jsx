import { useQuery } from '@tanstack/react-query';
import { Activity, Database, Server, Tv, Film, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default function SystemStatusWidget() {
  const { data: healthData } = useQuery({
    queryKey: ['system-health'],
    queryFn: async () => {
      const response = await api.get('/system/health');
      return response.data;
    },
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  const { data: statsData } = useQuery({
    queryKey: ['system-stats'],
    queryFn: async () => {
      const response = await api.get('/system/stats');
      return response.data;
    },
    refetchInterval: 60000, // Refresh every minute
  });

  const getStatusColor = (status) => {
    if (status === 'healthy' || status === 'ok') return 'text-green-600';
    if (status === 'degraded' || status === 'warning') return 'text-amber-600';
    return 'text-red-600';
  };

  const getStatusIcon = (status) => {
    if (status === 'healthy' || status === 'ok') return <CheckCircle className="h-5 w-5" />;
    if (status === 'degraded' || status === 'warning') return <AlertCircle className="h-5 w-5" />;
    return <XCircle className="h-5 w-5" />;
  };

  const getStatusBgColor = (status) => {
    if (status === 'healthy' || status === 'ok') return 'bg-green-50 border-green-200';
    if (status === 'degraded' || status === 'warning') return 'bg-amber-50 border-amber-200';
    return 'bg-red-50 border-red-200';
  };

  const overallStatus = healthData?.status || 'unknown';
  const dbStatus = healthData?.database || 'unknown';
  const redisStatus = healthData?.redis || 'unknown';

  return (
    <div className="bg-white rounded-lg shadow-md p-6 border border-gray-100">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-lg font-bold text-gray-900">System Status</h2>
        <div className={`flex items-center space-x-2 px-3 py-1.5 rounded-full border ${getStatusBgColor(overallStatus)}`}>
          <span className={getStatusColor(overallStatus)}>
            {getStatusIcon(overallStatus)}
          </span>
          <span className={`text-sm font-semibold ${getStatusColor(overallStatus)}`}>
            {overallStatus === 'healthy' || overallStatus === 'ok' ? 'Operational' : 
             overallStatus === 'degraded' || overallStatus === 'warning' ? 'Degraded' : 
             'Down'}
          </span>
        </div>
      </div>

      {/* Services Status */}
      <div className="space-y-3 mb-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Database className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-700">PostgreSQL</span>
          </div>
          <div className={`flex items-center space-x-1 ${getStatusColor(dbStatus)}`}>
            {getStatusIcon(dbStatus)}
            <span className="text-xs font-medium capitalize">{dbStatus}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Server className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-700">Redis</span>
          </div>
          <div className={`flex items-center space-x-1 ${getStatusColor(redisStatus)}`}>
            {getStatusIcon(redisStatus)}
            <span className="text-xs font-medium capitalize">{redisStatus}</span>
          </div>
        </div>

        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Activity className="h-4 w-4 text-gray-400" />
            <span className="text-sm text-gray-700">API Server</span>
          </div>
          <div className={`flex items-center space-x-1 ${getStatusColor(overallStatus)}`}>
            {getStatusIcon(overallStatus)}
            <span className="text-xs font-medium capitalize">{overallStatus}</span>
          </div>
        </div>
      </div>

      {/* Stats Summary */}
      {statsData && (
        <div className="pt-4 border-t border-gray-200">
          <div className="grid grid-cols-2 gap-4">
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Server className="h-4 w-4 text-brand-600" />
                <span className="text-2xl font-bold text-gray-900">{statsData.total_providers || 0}</span>
              </div>
              <p className="text-xs text-gray-600">Providers</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Tv className="h-4 w-4 text-accent-600" />
                <span className="text-2xl font-bold text-gray-900">{statsData.total_channels || 0}</span>
              </div>
              <p className="text-xs text-gray-600">Channels</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <Film className="h-4 w-4 text-ocean-600" />
                <span className="text-2xl font-bold text-gray-900">{statsData.total_vod_items || 0}</span>
              </div>
              <p className="text-xs text-gray-600">VOD Items</p>
            </div>
            <div className="text-center">
              <div className="flex items-center justify-center space-x-1 mb-1">
                <CheckCircle className="h-4 w-4 text-green-600" />
                <span className="text-2xl font-bold text-gray-900">{statsData.active_providers || 0}</span>
              </div>
              <p className="text-xs text-gray-600">Active</p>
            </div>
          </div>
        </div>
      )}

      {/* Version Info */}
      {healthData?.version && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <p className="text-xs text-gray-500 text-center">
            Version {healthData.version}
          </p>
        </div>
      )}
    </div>
  );
}
