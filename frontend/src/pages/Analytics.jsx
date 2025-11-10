import { useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { BarChart3, TrendingUp, Clock, Eye, Users as UsersIcon } from 'lucide-react'
import api from '../services/api'
import { useAuth } from '../contexts/AuthContext'

export default function Analytics() {
  const { isAdmin } = useAuth()
  const [dayRange, setDayRange] = useState(30)

  // User stats
  const { data: userStats } = useQuery({
    queryKey: ['analytics', 'userStats', dayRange],
    queryFn: async () => {
      const response = await api.get(`/api/analytics/stats?days=${dayRange}`)
      return response.data
    }
  })

  // Popular channels
  const { data: popularChannels } = useQuery({
    queryKey: ['analytics', 'popular', dayRange],
    queryFn: async () => {
      const response = await api.get(`/api/analytics/popular?days=${dayRange}`)
      return response.data
    }
  })

  // System stats (admin only)
  const { data: systemStats } = useQuery({
    queryKey: ['analytics', 'system'],
    queryFn: async () => {
      const response = await api.get('/api/analytics/admin/stats')
      return response.data
    },
    enabled: isAdmin
  })

  // Viewing history
  const { data: history } = useQuery({
    queryKey: ['analytics', 'history'],
    queryFn: async () => {
      const response = await api.get('/api/analytics/history?limit=20')
      return response.data
    }
  })

  const formatDuration = (seconds) => {
    if (!seconds) return '0m'
    const hours = Math.floor(seconds / 3600)
    const minutes = Math.floor((seconds % 3600) / 60)
    if (hours > 0) return `${hours}h ${minutes}m`
    return `${minutes}m`
  }

  return (
    <div className="px-4">
      <div className="sm:flex sm:items-center">
        <div className="sm:flex-auto">
          <h1 className="text-2xl font-semibold text-gray-900 flex items-center">
            <BarChart3 className="h-8 w-8 mr-2 text-blue-600" />
            Analytics
          </h1>
          <p className="mt-2 text-sm text-gray-700">
            Viewing statistics and trends
          </p>
        </div>
        <div className="mt-4 sm:mt-0 sm:ml-16">
          <select
            value={dayRange}
            onChange={(e) => setDayRange(Number(e.target.value))}
            className="rounded-md border-gray-300 py-2 pl-3 pr-10 text-base focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
          >
            <option value={7}>Last 7 days</option>
            <option value={30}>Last 30 days</option>
            <option value={90}>Last 90 days</option>
          </select>
        </div>
      </div>

      {/* System Stats (Admin Only) */}
      {isAdmin && systemStats && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">System Overview</h2>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-4">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Eye className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Views Today</dt>
                      <dd className="text-lg font-medium text-gray-900">{systemStats.total_views_today}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Views This Week</dt>
                      <dd className="text-lg font-medium text-gray-900">{systemStats.total_views_week}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <BarChart3 className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Views This Month</dt>
                      <dd className="text-lg font-medium text-gray-900">{systemStats.total_views_month}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <UsersIcon className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Active Users Today</dt>
                      <dd className="text-lg font-medium text-gray-900">{systemStats.unique_viewers_today}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Most Watched Today */}
          {systemStats.most_watched_today.length > 0 && (
            <div className="mt-6 bg-white shadow rounded-lg p-6">
              <h3 className="text-base font-medium text-gray-900 mb-4">Most Watched Today</h3>
              <div className="space-y-3">
                {systemStats.most_watched_today.map((channel, index) => (
                  <div key={channel.channel_id} className="flex items-center justify-between">
                    <div className="flex items-center">
                      <span className="text-lg font-bold text-gray-400 w-8">{index + 1}</span>
                      <span className="text-sm font-medium text-gray-900">{channel.channel_name}</span>
                    </div>
                    <div className="flex items-center space-x-4 text-sm text-gray-500">
                      <span>{channel.view_count} views</span>
                      <span>{channel.unique_viewers} viewers</span>
                      <span>{formatDuration(channel.total_watch_time_seconds)}</span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* User Stats */}
      {userStats && (
        <div className="mt-6">
          <h2 className="text-lg font-medium text-gray-900 mb-4">Your Viewing Stats</h2>
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-3">
            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Eye className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Total Views</dt>
                      <dd className="text-lg font-medium text-gray-900">{userStats.total_views}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <Clock className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Watch Time</dt>
                      <dd className="text-lg font-medium text-gray-900">
                        {formatDuration(userStats.total_watch_time_seconds)}
                      </dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>

            <div className="bg-white overflow-hidden shadow rounded-lg">
              <div className="p-5">
                <div className="flex items-center">
                  <div className="flex-shrink-0">
                    <TrendingUp className="h-6 w-6 text-gray-400" />
                  </div>
                  <div className="ml-5 w-0 flex-1">
                    <dl>
                      <dt className="text-sm font-medium text-gray-500 truncate">Channels Watched</dt>
                      <dd className="text-lg font-medium text-gray-900">{userStats.channels_watched}</dd>
                    </dl>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Popular Channels */}
      {popularChannels && popularChannels.length > 0 && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h3 className="text-base font-medium text-gray-900 mb-4">Most Popular Channels</h3>
          <div className="space-y-3">
            {popularChannels.map((channel, index) => (
              <div key={channel.channel_id} className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-lg font-bold text-gray-400 w-8">{index + 1}</span>
                  <span className="text-sm font-medium text-gray-900">{channel.channel_name}</span>
                </div>
                <div className="flex items-center space-x-4 text-sm text-gray-500">
                  <span>{channel.view_count} views</span>
                  <span>{formatDuration(channel.total_watch_time_seconds)}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Recent Viewing History */}
      {history && history.length > 0 && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h3 className="text-base font-medium text-gray-900 mb-4">Recent Viewing History</h3>
          <div className="overflow-hidden">
            <table className="min-w-full divide-y divide-gray-200">
              <thead>
                <tr>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Content
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Started
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Duration
                  </th>
                  <th className="px-3 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {history.map((item) => (
                  <tr key={item.id}>
                    <td className="px-3 py-4 text-sm text-gray-900">
                      {item.channel?.name || item.vod_movie?.title || item.vod_series?.title || 'Unknown'}
                    </td>
                    <td className="px-3 py-4 text-sm text-gray-500">
                      {new Date(item.started_at).toLocaleString()}
                    </td>
                    <td className="px-3 py-4 text-sm text-gray-500">
                      {formatDuration(item.duration_seconds)}
                    </td>
                    <td className="px-3 py-4 text-sm">
                      <span className={`inline-flex rounded-full px-2 text-xs font-semibold leading-5 ${
                        item.completed
                          ? 'bg-green-100 text-green-800'
                          : 'bg-yellow-100 text-yellow-800'
                      }`}>
                        {item.completed ? 'Completed' : 'In Progress'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
