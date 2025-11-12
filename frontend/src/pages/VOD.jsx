import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { getMovies, getSeries, generateSTRM } from '../services/api';
import { Film, Tv, Download, Search, Star } from 'lucide-react';
import toast from 'react-hot-toast';

export default function VOD() {
  const [activeTab, setActiveTab] = useState('movies');
  const [searchTerm, setSearchTerm] = useState('');
  const queryClient = useQueryClient();

  const { data: moviesData, isLoading: moviesLoading } = useQuery({
    queryKey: ['movies'],
    queryFn: async () => {
      const response = await getMovies();
      return response.data || [];
    },
    enabled: activeTab === 'movies',
  });

  const { data: seriesData, isLoading: seriesLoading } = useQuery({
    queryKey: ['series'],
    queryFn: async () => {
      const response = await getSeries();
      return response.data || [];
    },
    enabled: activeTab === 'series',
  });

  const generateMutation = useMutation({
    mutationFn: generateSTRM,
    onSuccess: () => {
      toast.success('STRM files generated successfully!');
      queryClient.invalidateQueries(['movies', 'series']);
    },
    onError: (error) => {
      toast.error(error?.response?.data?.detail || 'Failed to generate STRM files');
    },
  });

  const movies = (moviesData || []).filter(movie =>
    movie.title.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  const series = (seriesData || []).filter(show =>
    show.title.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent mb-2">
              Video on Demand
            </h1>
            <p className="text-gray-600">
              Browse movies and series from your providers
            </p>
          </div>
          <button
            onClick={() => generateMutation.mutate()}
            disabled={generateMutation.isPending}
            className="inline-flex items-center px-6 py-3 border border-transparent rounded-lg shadow-sm text-sm font-semibold text-white bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 disabled:opacity-50 transition-all"
          >
            <Download className="mr-2 h-5 w-5" />
            {generateMutation.isPending ? 'Generating...' : 'Generate STRM Files'}
          </button>
        </div>
      </div>

      {/* Tabs */}
      <div className="mb-6">
        <div className="flex items-center space-x-4 border-b border-gray-200">
          <button
            onClick={() => { setActiveTab('movies'); setSearchTerm(''); }}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'movies'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Film className="inline h-5 w-5 mr-2" />
            Movies ({moviesData?.length || 0})
          </button>
          <button
            onClick={() => { setActiveTab('series'); setSearchTerm(''); }}
            className={`px-6 py-3 font-medium text-sm border-b-2 transition-colors ${
              activeTab === 'series'
                ? 'border-brand-600 text-brand-600'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Tv className="inline h-5 w-5 mr-2" />
            Series ({seriesData?.length || 0})
          </button>
        </div>
      </div>

      {/* Search */}
      <div className="mb-6">
        <div className="relative max-w-md">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
          <input
            type="text"
            placeholder={`Search ${activeTab}...`}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
          />
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {activeTab === 'movies' ? movies.length : series.length} {activeTab}
      </div>

      {/* Movies Grid */}
      {activeTab === 'movies' && (
        <>
          {moviesLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 rounded-lg h-64 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : movies.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {movies.map((movie) => (
                <div key={movie.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-200 overflow-hidden group">
                  <div className="relative aspect-[2/3] bg-gradient-to-br from-gray-800 to-gray-900">
                    {movie.cover_url ? (
                      <img
                        src={movie.cover_url}
                        alt={movie.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Film className="h-12 w-12 text-gray-600" />
                      </div>
                    )}
                    {movie.rating && (
                      <div className="absolute top-2 right-2 bg-black/70 backdrop-blur-sm px-2 py-1 rounded-lg flex items-center space-x-1">
                        <Star className="h-4 w-4 text-yellow-400 fill-yellow-400" />
                        <span className="text-white text-xs font-bold">{movie.rating.toFixed(1)}</span>
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-sm text-gray-900 truncate" title={movie.title}>
                      {movie.title}
                    </h3>
                    <div className="flex items-center justify-between mt-1">
                      {movie.year && <span className="text-xs text-gray-600">{movie.year}</span>}
                      {movie.genre && <span className="text-xs text-gray-500 truncate ml-2">{movie.genre}</span>}
                    </div>
                    {movie.strm_file_path && (
                      <div className="mt-2 text-xs text-green-600 font-medium">STRM Available</div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Film className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No movies found</h3>
              <p className="text-gray-600">
                {searchTerm ? 'Try a different search term' : 'Add a provider with VOD content to get started'}
              </p>
            </div>
          )}
        </>
      )}

      {/* Series Grid */}
      {activeTab === 'series' && (
        <>
          {seriesLoading ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {[...Array(12)].map((_, i) => (
                <div key={i} className="animate-pulse">
                  <div className="bg-gray-200 rounded-lg h-64 mb-2"></div>
                  <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                </div>
              ))}
            </div>
          ) : series.length > 0 ? (
            <div className="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-5 xl:grid-cols-6 gap-4">
              {series.map((show) => (
                <div key={show.id} className="bg-white rounded-lg shadow-md hover:shadow-xl transition-shadow duration-200 overflow-hidden group">
                  <div className="relative aspect-[2/3] bg-gradient-to-br from-gray-800 to-gray-900">
                    {show.cover_url ? (
                      <img
                        src={show.cover_url}
                        alt={show.title}
                        className="w-full h-full object-cover"
                        onError={(e) => {
                          e.target.style.display = 'none';
                        }}
                      />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center">
                        <Tv className="h-12 w-12 text-gray-600" />
                      </div>
                    )}
                  </div>
                  <div className="p-3">
                    <h3 className="font-semibold text-sm text-gray-900 truncate" title={show.title}>
                      {show.title}
                    </h3>
                    <div className="flex items-center justify-between mt-1">
                      {show.year && <span className="text-xs text-gray-600">{show.year}</span>}
                      {show.genre && <span className="text-xs text-gray-500 truncate ml-2">{show.genre}</span>}
                    </div>
                    <div className="mt-2 text-xs text-gray-600">
                      {show.season_count} {show.season_count === 1 ? 'Season' : 'Seasons'} • {show.episode_count} Episodes
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-lg shadow-md p-12 text-center">
              <Tv className="h-16 w-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No series found</h3>
              <p className="text-gray-600">
                {searchTerm ? 'Try a different search term' : 'Add a provider with VOD content to get started'}
              </p>
            </div>
          )}
        </>
      )}
    </div>
  );
}
