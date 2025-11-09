import { useQuery } from '@tanstack/react-query'
import { getProviders, getVODStats, getHealthStatus } from '../services/api'
import { Radio, Tv, Film, Activity } from 'lucide-react'

function StatCard({ title, value, icon: Icon, color }) {
  return (
    <div className="bg-white overflow-hidden shadow rounded-lg">
      <div className="p-5">
        <div className="flex items-center">
          <div className={`flex-shrink-0 ${color}`}>
            <Icon className="h-6 w-6" />
          </div>
          <div className="ml-5 w-0 flex-1">
            <dl>
              <dt className="text-sm font-medium text-gray-500 truncate">{title}</dt>
              <dd className="text-lg font-semibold text-gray-900">{value}</dd>
            </dl>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function Dashboard() {
  const { data: providers } = useQuery({
    queryKey: ['providers'],
    queryFn: getProviders,
  })

  const { data: vodStats } = useQuery({
    queryKey: ['vodStats'],
    queryFn: getVODStats,
  })

  const { data: healthStatus } = useQuery({
    queryKey: ['healthStatus'],
    queryFn: getHealthStatus,
  })

  const activeProviders = providers?.data?.filter(p => p.enabled).length || 0
  const totalMovies = vodStats?.data?.total_movies || 0
  const totalSeries = vodStats?.data?.total_series || 0
  const activeStreams = healthStatus?.data?.active_streams || 0

  return (
    <div className="px-4 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-8">Dashboard</h1>

      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        <StatCard
          title="Active Providers"
          value={activeProviders}
          icon={Radio}
          color="text-blue-600"
        />
        <StatCard
          title="Active Streams"
          value={activeStreams}
          icon={Activity}
          color="text-green-600"
        />
        <StatCard
          title="VOD Movies"
          value={totalMovies}
          icon={Film}
          color="text-purple-600"
        />
        <StatCard
          title="VOD Series"
          value={totalSeries}
          icon={Tv}
          color="text-orange-600"
        />
      </div>

      <div className="mt-8 bg-white shadow rounded-lg p-6">
        <h2 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700">
            Sync All Providers
          </button>
          <button className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700">
            Run Health Check
          </button>
          <button className="bg-purple-600 text-white px-4 py-2 rounded-md hover:bg-purple-700">
            Generate STRM Files
          </button>
        </div>
      </div>
    </div>
  )
}
