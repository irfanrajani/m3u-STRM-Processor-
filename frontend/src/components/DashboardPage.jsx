import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Activity, Tv, Film, Server, TrendingUp } from 'lucide-react';
import SystemStatusWidget from './SystemStatusWidget';
import api from '../services/api';

function DashboardPage() {
  const { data: stats, isLoading } = useQuery({
    queryKey: ['system-stats'],
    queryFn: api.getSystemStats,
    refetchInterval: 10000,
  });

  const { data: providers = [] } = useQuery({
    queryKey: ['providers'],
    queryFn: api.getProviders,
  });

  const { data: channels = [] } = useQuery({
    queryKey: ['channels'],
    queryFn: api.getChannels,
  });

  const StatCard = ({ icon: Icon, title, value, subtitle, color, trend }) => (
    <div className={`bg-gradient-to-br ${color} rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 p-6 text-white`}>
      <div className="flex items-start justify-between mb-4">
        <div className="p-3 bg-white/20 rounded-lg backdrop-blur-sm">
          <Icon className="w-6 h-6" />
        </div>
        {trend && (
          <div className="flex items-center text-sm bg-white/20 px-2 py-1 rounded-full">
            <TrendingUp className="w-4 h-4 mr-1" />
            {trend}
          </div>
        )}
      </div>
      <div className="space-y-1">
        <p className="text-white/80 text-sm font-medium">{title}</p>
        <p className="text-3xl font-bold">
          {isLoading ? (
            <span className="animate-pulse">--</span>
          ) : (
            value
          )}
        </p>
        {subtitle && <p className="text-white/70 text-xs mt-1">{subtitle}</p>}
      </div>
    </div>
  );

  const enabledProviders = providers.filter(p => p.enabled).length;
  const activeChannels = channels.filter(c => c.enabled).length;
  const totalVod = (stats?.vod_movies || 0) + (stats?.vod_series || 0);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-brand-600 to-accent-600 rounded-xl shadow-glow p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2">Dashboard</h1>
            <p className="text-white/90">Monitor your IPTV infrastructure at a glance</p>
          </div>
          <Activity className="w-12 h-12 text-white/80" />
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          icon={Server}
          title="Active Providers"
          value={enabledProviders}
          subtitle={`${providers.length} total configured`}
          color="from-brand-500 to-brand-600"
          trend={enabledProviders > 0 ? `${Math.round((enabledProviders / Math.max(providers.length, 1)) * 100)}%` : null}
        />
        
        <StatCard
          icon={Tv}
          title="Live Channels"
          value={stats?.total_channels || channels.length}
          subtitle={`${activeChannels} enabled`}
          color="from-accent-500 to-accent-600"
        />
        
        <StatCard
          icon={Film}
          title="VOD Content"
          value={totalVod}
          subtitle={`${stats?.vod_movies || 0} movies, ${stats?.vod_series || 0} series`}
          color="from-ocean-500 to-ocean-600"
        />
        
        <StatCard
          icon={Activity}
          title="System Health"
          value={stats?.health_status === 'healthy' ? '100%' : stats?.health_status === 'degraded' ? '50%' : '0%'}
          subtitle={stats?.health_status || 'Unknown'}
          color={stats?.health_status === 'healthy' ? 'from-green-500 to-green-600' : 'from-yellow-500 to-yellow-600'}
        />
      </div>

      {/* System Status Widget */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <SystemStatusWidget />
        
        {/* Quick Actions */}
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Quick Actions</h2>
          <div className="space-y-3">
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-brand-50 to-accent-50 dark:from-brand-900/20 dark:to-accent-900/20 rounded-lg hover:shadow-md transition-all group">
              <span className="font-medium text-brand-700 dark:text-brand-300">Sync All Providers</span>
              <Server className="w-5 h-5 text-brand-600 dark:text-brand-400 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-accent-50 to-ocean-50 dark:from-accent-900/20 dark:to-ocean-900/20 rounded-lg hover:shadow-md transition-all group">
              <span className="font-medium text-accent-700 dark:text-accent-300">Process STRM Files</span>
              <Film className="w-5 h-5 text-accent-600 dark:text-accent-400 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="w-full flex items-center justify-between p-4 bg-gradient-to-r from-ocean-50 to-brand-50 dark:from-ocean-900/20 dark:to-brand-900/20 rounded-lg hover:shadow-md transition-all group">
              <span className="font-medium text-ocean-700 dark:text-ocean-300">Run Health Check</span>
              <Activity className="w-5 h-5 text-ocean-600 dark:text-ocean-400 group-hover:translate-x-1 transition-transform" />
            </button>
          </div>
        </div>
      </div>

      {/* Recent Activity (Placeholder) */}
      <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-6">
        <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">Recent Activity</h2>
        <div className="space-y-2 text-gray-600 dark:text-gray-400 text-sm">
          <p className="flex items-center">
            <span className="w-2 h-2 bg-green-500 rounded-full mr-3"></span>
            System started and ready
          </p>
          <p className="flex items-center">
            <span className="w-2 h-2 bg-blue-500 rounded-full mr-3"></span>
            {providers.length} provider{providers.length !== 1 ? 's' : ''} configured
          </p>
          <p className="flex items-center">
            <span className="w-2 h-2 bg-purple-500 rounded-full mr-3"></span>
            {channels.length} channel{channels.length !== 1 ? 's' : ''} available
          </p>
        </div>
      </div>
    </div>
  );
}

export default DashboardPage;
