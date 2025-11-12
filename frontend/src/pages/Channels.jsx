import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Tv, Search, Filter, Grid3x3, List, Signal } from 'lucide-react';
import { getChannels, getCategories } from '../services/api';
import ChannelDetailModal from '../components/ChannelDetailModal';

export default function Channels() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [enabledFilter, setEnabledFilter] = useState(null);
  const [selectedChannel, setSelectedChannel] = useState(null);

  const { data: categoriesData } = useQuery({
    queryKey: ['categories'],
    queryFn: async () => {
      const response = await getCategories();
      return response.data || [];
    },
  });

  const { data: channelsData, isLoading } = useQuery({
    queryKey: ['channels', selectedCategory, enabledFilter],
    queryFn: async () => {
      const params = {};
      if (selectedCategory) params.category = selectedCategory;
      if (enabledFilter !== null) params.enabled = enabledFilter;
      const response = await getChannels(params);
      return response.data || [];
    },
  });

  const filteredChannels = (channelsData || []).filter(channel =>
    channel.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const getQualityBadge = (streamCount) => {
    if (streamCount === 0) return { text: 'No Streams', color: 'gray', iconClass: 'text-gray-500', textClass: 'text-gray-700' };
    if (streamCount === 1) return { text: 'SD', color: 'yellow', iconClass: 'text-yellow-500', textClass: 'text-yellow-700' };
    if (streamCount === 2) return { text: 'HD', color: 'blue', iconClass: 'text-blue-500', textClass: 'text-blue-700' };
    return { text: '4K', color: 'purple', iconClass: 'text-purple-500', textClass: 'text-purple-700' };
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent mb-2">
          Channels
        </h1>
        <p className="text-gray-600">
          Browse and manage your IPTV channels
        </p>
      </div>

      {/* Filters Bar */}
      <div className="bg-white rounded-lg shadow-md p-4 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <div className="md:col-span-2">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
              <input
                type="text"
                placeholder="Search channels..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              />
            </div>
          </div>

          {/* Category Filter */}
          <div>
            <select
              value={selectedCategory}
              onChange={(e) => setSelectedCategory(e.target.value)}
              className="w-full px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="">All Categories</option>
              {(categoriesData || []).map((cat) => (
                <option key={cat.name} value={cat.name}>
                  {cat.name} ({cat.count})
                </option>
              ))}
            </select>
          </div>

          {/* Status Filter */}
          <div className="flex items-center space-x-2">
            <select
              value={enabledFilter === null ? '' : String(enabledFilter)}
              onChange={(e) => setEnabledFilter(e.target.value === '' ? null : e.target.value === 'true')}
              className="flex-1 px-4 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="">All Status</option>
              <option value="true">Enabled</option>
              <option value="false">Disabled</option>
            </select>

            {/* View Toggle */}
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setViewMode('grid')}
                className={`p-2 rounded ${viewMode === 'grid' ? 'bg-white shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
              >
                <Grid3x3 className="h-5 w-5" />
              </button>
              <button
                onClick={() => setViewMode('list')}
                className={`p-2 rounded ${viewMode === 'list' ? 'bg-white shadow-sm' : 'text-gray-600 hover:text-gray-900'}`}
              >
                <List className="h-5 w-5" />
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Results Count */}
      <div className="mb-4 text-sm text-gray-600">
        Showing {filteredChannels.length} channels
        {selectedCategory && ` in ${selectedCategory}`}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {[...Array(8)].map((_, i) => (
            <div key={i} className="bg-white rounded-lg shadow-md p-4 animate-pulse">
              <div className="h-32 bg-gray-200 rounded mb-4"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-3 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      )}

      {/* Grid View */}
      {!isLoading && viewMode === 'grid' && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
          {filteredChannels.map((channel) => {
            const quality = getQualityBadge(channel.stream_count);
            return (
              <div
                key={channel.id}
                onClick={() => setSelectedChannel(channel)}
                className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden group cursor-pointer"
              >
                {/* Channel Logo */}
                <div className="relative h-32 bg-gradient-to-br from-gray-100 to-gray-200 flex items-center justify-center">
                  {channel.logo_url ? (
                    <img
                      src={channel.logo_url}
                      alt={channel.name}
                      className="max-h-full max-w-full object-contain p-4"
                      onError={(e) => {
                        e.target.style.display = 'none';
                        e.target.parentElement.querySelector('.fallback-icon').style.display = 'flex';
                      }}
                    />
                  ) : null}
                  <div className="fallback-icon absolute inset-0 flex items-center justify-center" style={{ display: channel.logo_url ? 'none' : 'flex' }}>
                    <Tv className="h-12 w-12 text-gray-400" />
                  </div>

                  {/* Status Badge */}
                  <div className="absolute top-2 right-2">
                    <span className={`px-2 py-1 text-xs font-semibold rounded-full ${
                      channel.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                    }`}>
                      {channel.enabled ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                </div>

                {/* Channel Info */}
                <div className="p-4">
                  <h3 className="font-semibold text-gray-900 mb-2 truncate">
                    {channel.name}
                  </h3>

                  <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-600">
                      {channel.category || 'Uncategorized'}
                    </span>
                    <div className="flex items-center space-x-1">
                      <Signal className={`h-4 w-4 ${quality.iconClass}`} />
                      <span className={`text-xs font-medium ${quality.textClass}`}>
                        {quality.text}
                      </span>
                    </div>
                  </div>

                  {channel.region && (
                    <div className="mt-2 text-xs text-gray-500">
                      {channel.region}
                    </div>
                  )}

                  {/* Stream Count */}
                  <div className="mt-3 pt-3 border-t border-gray-100">
                    <div className="flex items-center justify-between text-xs text-gray-600">
                      <span>{channel.stream_count} stream(s)</span>
                      {channel.epg_id && (
                        <span className="bg-blue-50 text-blue-700 px-2 py-0.5 rounded">
                          EPG
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      )}

      {/* List View */}
      {!isLoading && viewMode === 'list' && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Channel
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Category
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Region
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Streams
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredChannels.map((channel) => {
                const quality = getQualityBadge(channel.stream_count);
                return (
                  <tr 
                    key={channel.id} 
                    onClick={() => setSelectedChannel(channel)}
                    className="hover:bg-gray-50 cursor-pointer"
                  >
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {channel.logo_url ? (
                          <img src={channel.logo_url} alt={channel.name} className="h-10 w-10 rounded object-contain mr-3" />
                        ) : (
                          <div className="h-10 w-10 rounded bg-gray-100 flex items-center justify-center mr-3">
                            <Tv className="h-5 w-5 text-gray-400" />
                          </div>
                        )}
                        <div>
                          <div className="text-sm font-medium text-gray-900">{channel.name}</div>
                          {channel.epg_id && (
                            <div className="text-xs text-blue-600">EPG Available</div>
                          )}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {channel.category || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                      {channel.region || '-'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center space-x-2">
                        <Signal className={`h-4 w-4 text-${quality.color}-500`} />
                        <span className="text-sm text-gray-900">{channel.stream_count}</span>
                        <span className={`text-xs text-${quality.color}-700`}>({quality.text})</span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                        channel.enabled ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
                      }`}>
                        {channel.enabled ? 'Active' : 'Inactive'}
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}

      {/* Empty State */}
      {!isLoading && filteredChannels.length === 0 && (
        <div className="bg-white rounded-lg shadow-md p-12 text-center">
          <Tv className="h-16 w-16 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No channels found</h3>
          <p className="text-gray-600 mb-4">
            {searchTerm || selectedCategory
              ? 'Try adjusting your filters or search term'
              : 'Add a provider and sync to get started'}
          </p>
        </div>
      )}

      {/* Channel Detail Modal */}
      {selectedChannel && (
        <ChannelDetailModal
          channel={selectedChannel}
          onClose={() => setSelectedChannel(null)}
        />
      )}
    </div>
  );
}
