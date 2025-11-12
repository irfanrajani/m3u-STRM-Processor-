import { useState } from 'react';
import { useQuery, useMutation } from '@tantml:react-query';
import { Activity, Tv, Radio, Server, TrendingUp, Users, HardDrive, AlertCircle, CheckCircle, Zap, RefreshCw } from 'lucide-react';
import axios from 'axios';
import { syncAllProviders, generateSTRM, triggerHealthCheck } from '../services/api';

const API_BASE_URL = 'http://localhost:8000/api';

export default function Dashboard() {
  const [refreshInterval, setRefreshInterval] = useState(5000); // 5 seconds

  // Fetch real-time stats
  const { data: realtimeStats, isLoading, refetch } = useQuery({
    queryKey: ['realtimeStats'],
    queryFn: async () => {
      const response = await axios.get(`${API_BASE_URL}/system/stats/realtime`);
      return response.data;
    },
    refetchInterval: refreshInterval,
  });

  const syncAllMutation = useMutation({
    mutationFn: syncAllProviders,
    onSuccess: () => {
      alert('Sync started! This may take several minutes.');
      refetch();
    },
  });

  const healthCheckMutation = useMutation({
    mutationFn: triggerHealthCheck,
    onSuccess: () => {
      alert('Health check started! This may take several minutes.');
      refetch();
    },
  });

  const strmMutation = useMutation({
    mutationFn: generateSTRM,
    onSuccess: () => {
      alert('STRM generation started! Check the output folder when complete.');
    },
  });

  if (isLoading || !realtimeStats) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading dashboard...</p>
        </div>
      </div>
    );
  }

  const {
    streaming,
    channels,
    streams,
    providers,
    deduplication,
  } = realtimeStats;

  // Calculate bandwidth savings
  const bandwidthSavingsPercent = streaming.bandwidth_saved_percentage || 0;
  const bandwidthSavedMB = streaming.bandwidth_saved_mb || 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 p-6">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Dashboard</h1>
          <p className="text-gray-600">Real-time system monitoring and statistics</p>
        </div>
        <button
          onClick={() => refetch()}
          className="flex items-center gap-2 px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
        >
          <RefreshCw className="w-4 h-4" />
          Refresh
        </button>
      </div>

      {/* Main Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {/* Active Streams */}
        <StatCard
          title="Active Streams"
          value={streaming.active_streams}
          subtitle={`${streaming.active_clients} clients watching`}
          icon={<Radio className="w-8 h-8 text-blue-500" />}
          trend={streaming.active_streams > 0 ? 'up' : 'neutral'}
          color="blue"
        />

        {/* Total Channels */}
        <StatCard
          title="Total Channels"
          value={channels.total}
          subtitle={`${channels.merged_count} with backups`}
          icon={<Tv className="w-8 h-8 text-purple-500" />}
          color="purple"
        />

        {/* Stream Health */}
        <StatCard
          title="Stream Health"
          value={`${streams.health_percentage}%`}
          subtitle={`${streams.healthy}/${streams.active} healthy`}
          icon={
            streams.health_percentage >= 90 ? (
              <CheckCircle className="w-8 h-8 text-green-500" />
            ) : (
              <AlertCircle className="w-8 h-8 text-yellow-500" />
            )
          }
          trend={streams.health_percentage >= 90 ? 'up' : 'down'}
          color={streams.health_percentage >= 90 ? 'green' : 'yellow'}
        />

        {/* Bandwidth Saved */}
        <StatCard
          title="Bandwidth Saved"
          value={`${bandwidthSavingsPercent}%`}
          subtitle={`${bandwidthSavedMB.toFixed(1)} MB saved`}
          icon={<Zap className="w-8 h-8 text-yellow-500" />}
          trend="up"
          color="yellow"
        />
      </div>

      {/* Deduplication Stats */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <TrendingUp className="w-6 h-6 text-green-500" />
            Automatic Deduplication
          </h2>
          <div className="text-sm text-gray-500">
            Processing efficiency
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center">
            <div className="text-4xl font-bold text-blue-600 mb-2">
              {deduplication.total_streams_imported.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600 font-medium">Streams Imported</div>
          </div>

          <div className="text-center">
            <div className="text-6xl font-bold text-gray-400 mb-2">→</div>
          </div>

          <div className="text-center">
            <div className="text-4xl font-bold text-green-600 mb-2">
              {deduplication.unique_channels.toLocaleString()}
            </div>
            <div className="text-sm text-gray-600 font-medium">Unique Channels</div>
          </div>
        </div>

        <div className="mt-6 p-4 bg-green-50 rounded-lg border border-green-200">
          <div className="flex items-center justify-center gap-2">
            <CheckCircle className="w-5 h-5 text-green-600" />
            <span className="text-green-900 font-semibold">
              {deduplication.duplicates_merged.toLocaleString()} duplicate streams merged automatically
            </span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <button
            onClick={() => syncAllMutation.mutate()}
            disabled={syncAllMutation.isPending}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 disabled:opacity-50 font-medium transition-colors"
          >
            {syncAllMutation.isPending ? 'Syncing...' : 'Sync All Providers'}
          </button>
          <button
            onClick={() => healthCheckMutation.mutate()}
            disabled={healthCheckMutation.isPending}
            className="bg-green-600 text-white px-6 py-3 rounded-lg hover:bg-green-700 disabled:opacity-50 font-medium transition-colors"
          >
            {healthCheckMutation.isPending ? 'Checking...' : 'Run Health Check'}
          </button>
          <button
            onClick={() => strmMutation.mutate()}
            disabled={strmMutation.isPending}
            className="bg-purple-600 text-white px-6 py-3 rounded-lg hover:bg-purple-700 disabled:opacity-50 font-medium transition-colors"
          >
            {strmMutation.isPending ? 'Generating...' : 'Generate STRM Files'}
          </button>
        </div>
      </div>

      {/* Active Streams Table */}
      {streaming.streams && streaming.streams.length > 0 && (
        <div className="bg-white rounded-xl shadow-sm p-6 mb-8 border border-gray-200">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <Activity className="w-6 h-6 text-blue-500" />
            Active Streams
          </h2>
          
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b border-gray-200">
                  <th className="text-left p-3 text-sm font-semibold text-gray-700">Channel ID</th>
                  <th className="text-left p-3 text-sm font-semibold text-gray-700">Clients</th>
                  <th className="text-left p-3 text-sm font-semibold text-gray-700">Bandwidth</th>
                  <th className="text-left p-3 text-sm font-semibold text-gray-700">Uptime</th>
                  <th className="text-left p-3 text-sm font-semibold text-gray-700">Status</th>
                </tr>
              </thead>
              <tbody>
                {streaming.streams.map((stream) => (
                  <tr key={stream.channel_id} className="border-b border-gray-100 hover:bg-gray-50">
                    <td className="p-3 text-sm font-mono text-gray-900">#{stream.channel_id}</td>
                    <td className="p-3 text-sm">
                      <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-100 text-blue-700 rounded-full">
                        <Users className="w-3 h-3" />
                        {stream.clients}
                      </span>
                    </td>
                    <td className="p-3 text-sm font-medium text-gray-700">
                      {stream.bandwidth_mb.toFixed(2)} MB
                    </td>
                    <td className="p-3 text-sm text-gray-600">
                      {Math.floor(stream.uptime_seconds / 60)}m {Math.floor(stream.uptime_seconds % 60)}s
                    </td>
                    <td className="p-3">
                      {stream.is_alive ? (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
                          <CheckCircle className="w-3 h-3" />
                          Live
                        </span>
                      ) : (
                        <span className="inline-flex items-center gap-1 px-2 py-1 bg-red-100 text-red-700 rounded-full text-xs font-medium">
                          <AlertCircle className="w-3 h-3" />
                          {stream.error || 'Error'}
                        </span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {/* System Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        {/* Providers */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Providers</h3>
            <Server className="w-6 h-6 text-gray-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total</span>
              <span className="font-bold text-gray-900">{providers.total}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active</span>
              <span className="font-bold text-green-600">{providers.active}</span>
            </div>
          </div>
        </div>

        {/* Streams */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Streams</h3>
            <Radio className="w-6 h-6 text-gray-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Total</span>
              <span className="font-bold text-gray-900">{streams.total}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Active</span>
              <span className="font-bold text-blue-600">{streams.active}</span>
            </div>
          </div>
        </div>

        {/* Performance */}
        <div className="bg-white rounded-xl shadow-sm p-6 border border-gray-200">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">Performance</h3>
            <HardDrive className="w-6 h-6 text-gray-400" />
          </div>
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Peak Streams</span>
              <span className="font-bold text-purple-600">{streaming.peak_concurrent_streams}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-gray-600">Clients Served</span>
              <span className="font-bold text-blue-600">{streaming.total_clients_served}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

// Stat Card Component
function StatCard({ title, value, subtitle, icon, trend, color }) {
  const colorClasses = {
    blue: 'bg-blue-50 border-blue-200',
    purple: 'bg-purple-50 border-purple-200',
    green: 'bg-green-50 border-green-200',
    yellow: 'bg-yellow-50 border-yellow-200',
  };

  return (
    <div className={`${colorClasses[color]} rounded-xl shadow-sm p-6 border`}>
      <div className="flex items-start justify-between">
        <div className="flex-1">
          <p className="text-sm font-medium text-gray-600 mb-2">{title}</p>
          <p className="text-3xl font-bold text-gray-900 mb-1">{value}</p>
          <p className="text-sm text-gray-500">{subtitle}</p>
        </div>
        <div className="ml-4">{icon}</div>
      </div>
    </div>
  );
}
