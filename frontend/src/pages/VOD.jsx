import { useState } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { getMovies, getSeries, generateSTRM } from '../services/api'
import { Film, Tv, Download } from 'lucide-react'

export default function VOD() {
  const [activeTab, setActiveTab] = useState('movies')
  const queryClient = useQueryClient()

  const { data: moviesData, isLoading: moviesLoading } = useQuery({
    queryKey: ['movies'],
    queryFn: getMovies,
    enabled: activeTab === 'movies',
  })

  const { data: seriesData, isLoading: seriesLoading } = useQuery({
    queryKey: ['series'],
    queryFn: getSeries,
    enabled: activeTab === 'series',
  })

  const generateMutation = useMutation({
    mutationFn: generateSTRM,
    onSuccess: () => {
      queryClient.invalidateQueries(['movies', 'series'])
    },
  })

  const movies = moviesData?.data || []
  const series = seriesData?.data || []

  return (
    <div className="px-4 sm:px-0">
      <div className="sm:flex sm:items-center sm:justify-between mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Video on Demand</h1>
        <button
          onClick={() => generateMutation.mutate()}
          disabled={generateMutation.isPending}
          className="mt-4 sm:mt-0 inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-purple-600 hover:bg-purple-700 disabled:opacity-50"
        >
          <Download className="mr-2 h-4 w-4" />
          {generateMutation.isPending ? 'Generating...' : 'Generate STRM Files'}
        </button>
      </div>

      <div className="mb-6">
        <nav className="flex space-x-4">
          <button
            onClick={() => setActiveTab('movies')}
            className={`px-3 py-2 font-medium text-sm rounded-md ${
              activeTab === 'movies'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Film className="inline h-4 w-4 mr-2" />
            Movies ({movies.length})
          </button>
          <button
            onClick={() => setActiveTab('series')}
            className={`px-3 py-2 font-medium text-sm rounded-md ${
              activeTab === 'series'
                ? 'bg-blue-100 text-blue-700'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            <Tv className="inline h-4 w-4 mr-2" />
            Series ({series.length})
          </button>
        </nav>
      </div>

      {activeTab === 'movies' ? (
        moviesLoading ? (
          <div className="text-center py-10">Loading movies...</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {movies.map((movie) => (
              <div key={movie.id} className="bg-white rounded-lg shadow overflow-hidden">
                {movie.cover_url && (
                  <img
                    src={movie.cover_url}
                    alt={movie.title}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-3">
                  <h3 className="font-medium text-sm text-gray-900 truncate">{movie.title}</h3>
                  <p className="text-xs text-gray-500">{movie.year}</p>
                  <p className="text-xs text-gray-500">{movie.genre}</p>
                </div>
              </div>
            ))}
          </div>
        )
      ) : (
        seriesLoading ? (
          <div className="text-center py-10">Loading series...</div>
        ) : (
          <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 gap-4">
            {series.map((show) => (
              <div key={show.id} className="bg-white rounded-lg shadow overflow-hidden">
                {show.cover_url && (
                  <img
                    src={show.cover_url}
                    alt={show.title}
                    className="w-full h-48 object-cover"
                  />
                )}
                <div className="p-3">
                  <h3 className="font-medium text-sm text-gray-900 truncate">{show.title}</h3>
                  <p className="text-xs text-gray-500">{show.year}</p>
                  <p className="text-xs text-gray-500">
                    {show.season_count} seasons • {show.episode_count} episodes
                  </p>
                </div>
              </div>
            ))}
          </div>
        )
      )}
    </div>
  )
}
