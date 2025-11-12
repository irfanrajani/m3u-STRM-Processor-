import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Star, Grid3x3, List, Search, Filter, Tv, Film, Heart } from 'lucide-react';
import api from '../services/api';
import toast from 'react-hot-toast';

export default function Favorites() {
  const queryClient = useQueryClient();
  const [viewMode, setViewMode] = useState('grid');
  const [searchQuery, setSearchQuery] = useState('');
  const [typeFilter, setTypeFilter] = useState('all'); // all, channels, vod

  const { data: favorites = [], isLoading } = useQuery({
    queryKey: ['favorites'],
    queryFn: api.getFavorites,
  });

  const removeFavoriteMutation = useMutation({
    mutationFn: ({ type, id }) => api.removeFavorite(type, id),
    onSuccess: () => {
      queryClient.invalidateQueries(['favorites']);
      toast.success('Removed from favorites');
    },
    onError: () => {
      toast.error('Failed to remove favorite');
    },
  });

  const handleRemoveFavorite = (item) => {
    const type = item.stream_count !== undefined ? 'channel' : 'vod';
    removeFavoriteMutation.mutate({ type, id: item.id });
  };

  // Filter favorites
  const filteredFavorites = favorites.filter((item) => {
    const matchesSearch = item.name?.toLowerCase().includes(searchQuery.toLowerCase());
    const matchesType =
      typeFilter === 'all' ||
      (typeFilter === 'channels' && item.stream_count !== undefined) ||
      (typeFilter === 'vod' && item.stream_count === undefined);
    return matchesSearch && matchesType;
  });

  const channelCount = favorites.filter((f) => f.stream_count !== undefined).length;
  const vodCount = favorites.filter((f) => f.stream_count === undefined).length;

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600 mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading favorites...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-gradient-to-r from-brand-600 to-accent-600 rounded-xl shadow-glow p-8 text-white">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold mb-2 flex items-center">
              <Heart className="w-8 h-8 mr-3 fill-current" />
              My Favorites
            </h1>
            <p className="text-white/90">
              {favorites.length} favorite{favorites.length !== 1 ? 's' : ''} ({channelCount} channels, {vodCount} VOD)
            </p>
          </div>
        </div>
      </div>

      {/* Filters & Controls */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-4">
        <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4">
          {/* Search */}
          <div className="relative flex-1 max-w-md">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search favorites..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            />
          </div>

          {/* Type Filter */}
          <div className="flex items-center gap-2">
            <Filter className="w-5 h-5 text-gray-500" />
            <select
              value={typeFilter}
              onChange={(e) => setTypeFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-brand-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
            >
              <option value="all">All ({favorites.length})</option>
              <option value="channels">Channels ({channelCount})</option>
              <option value="vod">VOD ({vodCount})</option>
            </select>
          </div>

          {/* View Mode Toggle */}
          <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                viewMode === 'grid'
                  ? 'bg-white dark:bg-gray-600 text-brand-600 dark:text-brand-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <Grid3x3 className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-1.5 rounded-md transition-all ${
                viewMode === 'list'
                  ? 'bg-white dark:bg-gray-600 text-brand-600 dark:text-brand-400 shadow-sm'
                  : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* Favorites Content */}
      {filteredFavorites.length === 0 ? (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-12 text-center">
          <Heart className="w-16 h-16 mx-auto text-gray-300 dark:text-gray-600 mb-4" />
          <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            {searchQuery || typeFilter !== 'all' ? 'No favorites found' : 'No favorites yet'}
          </h3>
          <p className="text-gray-600 dark:text-gray-400">
            {searchQuery || typeFilter !== 'all'
              ? 'Try adjusting your filters'
              : 'Add channels or VOD content to your favorites to see them here'}
          </p>
        </div>
      ) : viewMode === 'grid' ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {filteredFavorites.map((item) => {
            const isChannel = item.stream_count !== undefined;
            return (
              <div
                key={`${isChannel ? 'channel' : 'vod'}-${item.id}`}
                className="bg-white dark:bg-gray-800 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 overflow-hidden group"
              >
                {/* Thumbnail */}
                <div className="relative aspect-video bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-700 dark:to-gray-800">
                  {item.logo_url || item.cover_url ? (
                    <img
                      src={item.logo_url || item.cover_url}
                      alt={item.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="flex items-center justify-center h-full">
                      {isChannel ? (
                        <Tv className="w-12 h-12 text-gray-400" />
                      ) : (
                        <Film className="w-12 h-12 text-gray-400" />
                      )}
                    </div>
                  )}
                  {/* Remove button overlay */}
                  <button
                    onClick={() => handleRemoveFavorite(item)}
                    className="absolute top-2 right-2 p-2 bg-red-600/90 hover:bg-red-700 text-white rounded-full opacity-0 group-hover:opacity-100 transition-opacity"
                    title="Remove from favorites"
                  >
                    <Heart className="w-4 h-4 fill-current" />
                  </button>
                </div>

                {/* Content */}
                <div className="p-4">
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-semibold text-gray-900 dark:text-white line-clamp-2 flex-1">
                      {item.name}
                    </h3>
                  </div>
                  <div className="flex items-center gap-2">
                    <span
                      className={`inline-flex items-center px-2 py-1 rounded-full text-xs font-medium ${
                        isChannel
                          ? 'bg-brand-100 text-brand-800 dark:bg-brand-900/30 dark:text-brand-300'
                          : 'bg-accent-100 text-accent-800 dark:bg-accent-900/30 dark:text-accent-300'
                      }`}
                    >
                      {isChannel ? <Tv className="w-3 h-3 mr-1" /> : <Film className="w-3 h-3 mr-1" />}
                      {isChannel ? 'Channel' : 'VOD'}
                    </span>
                    {item.category && (
                      <span className="text-xs text-gray-500 dark:text-gray-400 truncate">
                        {item.category}
                      </span>
                    )}
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead className="bg-gray-50 dark:bg-gray-700">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Type
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200 dark:divide-gray-700">
              {filteredFavorites.map((item) => {
                const isChannel = item.stream_count !== undefined;
                return (
                  <tr
                    key={`${isChannel ? 'channel' : 'vod'}-${item.id}`}
                    className="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {item.logo_url || item.cover_url ? (
                          <img
                            src={item.logo_url || item.cover_url}
                            alt={item.name}
                            className="w-10 h-10 rounded object-cover mr-3"
                          />
                        ) : (
                          <div className="w-10 h-10 rounded bg-gray-200 dark:bg-gray-700 flex items-center justify-center mr-3">
                            {isChannel ? (
                              <Tv className="w-5 h-5 text-gray-400" />
                            ) : (
                              <Film className="w-5 h-5 text-gray-400" />
                            )}
                          </div>
                        )}
                        <span className="font-medium text-gray-900 dark:text-white">{item.name}</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span
                        className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          isChannel
                            ? 'bg-brand-100 text-brand-800 dark:bg-brand-900/30 dark:text-brand-300'
                            : 'bg-accent-100 text-accent-800 dark:bg-accent-900/30 dark:text-accent-300'
                        }`}
                      >
                        {isChannel ? 'Channel' : 'VOD'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                      {item.category || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm">
                      <button
                        onClick={() => handleRemoveFavorite(item)}
                        className="text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                      >
                        <Heart className="w-5 h-5 fill-current" />
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
