import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import {
  Grid, List, Search, ChevronRight, AlertCircle, CheckCircle,
  Activity, Tv, TrendingUp, Filter, Settings as SettingsIcon,
  Users, Layers, Split, GitMerge, X
} from 'lucide-react';
import { getChannels } from '../services/api';
import axios from 'axios';

// Create API client with auth
const api = axios.create({
  baseURL: '/api',
});

// Add auth token to requests
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default function ChannelsPage() {
  const [viewMode, setViewMode] = useState('grid'); // 'grid' or 'list'
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [selectedChannel, setSelectedChannel] = useState(null);
  const queryClient = useQueryClient();

  // Fetch channels
  const { data: channelsData, isLoading } = useQuery({
    queryKey: ['channels', searchTerm, selectedCategory],
    queryFn: async () => {
      const params = {};
      if (searchTerm) params.search = searchTerm;
      if (selectedCategory !== 'all') params.category = selectedCategory;
      
      const response = await getChannels(params);
      return response.data;
    },
  });

  const channels = channelsData || [];
  const categories = [...new Set(channels.map(c => c.category).filter(Boolean))];

  // Fetch merge details when channel selected
  const { data: mergeDetails } = useQuery({
    queryKey: ['mergeDetails', selectedChannel?.id],
    queryFn: async () => {
      const response = await api.get(`/channels/${selectedChannel.id}/merge-details`);
      return response.data;
    },
    enabled: !!selectedChannel,
  });

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6 flex items-center justify-center">
        <div className="text-center">
          <Activity className="w-12 h-12 text-blue-500 animate-spin mx-auto mb-4" />
          <p className="text-gray-600">Loading channels...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
      {/* Header */}
      <div className="bg-white border-b border-gray-200 px-6 py-4">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Channels</h1>
            <p className="text-gray-600 mt-1">
              {channels.length.toLocaleString()} channels • 
              {channels.filter(c => c.stream_count > 1).length.toLocaleString()} with multiple streams
            </p>
          </div>

          {/* View Mode Toggle */}
          <div className="flex items-center gap-2 bg-gray-100 rounded-lg p-1">
            <button
              onClick={() => setViewMode('grid')}
              className={`px-3 py-2 rounded-md transition-colors ${
                viewMode === 'grid'
                  ? 'bg-white shadow-sm text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <Grid className="w-5 h-5" />
            </button>
            <button
              onClick={() => setViewMode('list')}
              className={`px-3 py-2 rounded-md transition-colors ${
                viewMode === 'list'
                  ? 'bg-white shadow-sm text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              <List className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Search and Filters */}
        <div className="flex gap-4">
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              placeholder="Search channels..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <select
            value={selectedCategory}
            onChange={(e) => setSelectedCategory(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="all">All Categories</option>
            {categories.map(cat => (
              <option key={cat} value={cat}>{cat}</option>
            ))}
          </select>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex">
        {/* Channel List/Grid */}
        <div className={`flex-1 p-6 ${selectedChannel ? 'pr-0' : ''}`}>
          {viewMode === 'grid' ? (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {channels.map(channel => (
                <ChannelCard
                  key={channel.id}
                  channel={channel}
                  onClick={() => setSelectedChannel(channel)}
                  isSelected={selectedChannel?.id === channel.id}
                />
              ))}
            </div>
          ) : (
            <div className="bg-white rounded-xl shadow-sm border border-gray-200">
              {channels.map((channel, idx) => (
                <ChannelRow
                  key={channel.id}
                  channel={channel}
                  onClick={() => setSelectedChannel(channel)}
                  isSelected={selectedChannel?.id === channel.id}
                  isLast={idx === channels.length - 1}
                />
              ))}
            </div>
          )}
        </div>

        {/* Detail Side Panel */}
        {selectedChannel && mergeDetails && (
          <ChannelDetailPanel
            channel={selectedChannel}
            mergeDetails={mergeDetails}
            onClose={() => setSelectedChannel(null)}
            onUpdate={() => {
              queryClient.invalidateQueries(['channels']);
              queryClient.invalidateQueries(['mergeDetails']);
            }}
          />
        )}
      </div>
    </div>
  );
}

// Channel Card Component (Grid View)
function ChannelCard({ channel, onClick, isSelected }) {
  const hasMergedStreams = channel.stream_count > 1;

  return (
    <div
      onClick={onClick}
      className={`bg-white rounded-xl p-4 border-2 cursor-pointer transition-all hover:shadow-lg ${
        isSelected ? 'border-blue-500 shadow-lg' : 'border-gray-200'
      }`}
    >
      {/* Channel Logo */}
      {channel.logo_url ? (
        <img
          src={channel.logo_url}
          alt={channel.name}
          className="w-full h-24 object-contain mb-3 rounded-lg bg-gray-50"
        />
      ) : (
        <div className="w-full h-24 bg-gradient-to-br from-blue-100 to-purple-100 rounded-lg mb-3 flex items-center justify-center">
          <Tv className="w-12 h-12 text-blue-600" />
        </div>
      )}

      {/* Channel Name */}
      <h3 className="font-semibold text-gray-900 mb-2 truncate" title={channel.name}>
        {channel.name}
      </h3>

      {/* Metadata */}
      <div className="flex items-center justify-between text-sm">
        <span className="text-gray-500">{channel.category || 'Uncategorized'}</span>
        
        {hasMergedStreams && (
          <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-100 text-green-700 rounded-full text-xs font-medium">
            <Layers className="w-3 h-3" />
            {channel.stream_count} streams
          </span>
        )}
      </div>

      {/* Region/Variant Tags */}
      <div className="flex gap-1 mt-2">
        {channel.region && (
          <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
            {channel.region}
          </span>
        )}
        {channel.variant && (
          <span className="px-2 py-0.5 bg-purple-100 text-purple-700 rounded text-xs">
            {channel.variant}
          </span>
        )}
      </div>
    </div>
  );
}

// Channel Row Component (List View)
function ChannelRow({ channel, onClick, isSelected, isLast }) {
  const hasMergedStreams = channel.stream_count > 1;

  return (
    <div
      onClick={onClick}
      className={`flex items-center gap-4 p-4 cursor-pointer transition-colors hover:bg-gray-50 ${
        isSelected ? 'bg-blue-50 border-l-4 border-l-blue-500' : ''
      } ${!isLast ? 'border-b border-gray-100' : ''}`}
    >
      {/* Logo */}
      {channel.logo_url ? (
        <img src={channel.logo_url} alt={channel.name} className="w-12 h-12 object-contain rounded" />
      ) : (
        <div className="w-12 h-12 bg-gradient-to-br from-blue-100 to-purple-100 rounded flex items-center justify-center">
          <Tv className="w-6 h-6 text-blue-600" />
        </div>
      )}

      {/* Channel Info */}
      <div className="flex-1 min-w-0">
        <h3 className="font-semibold text-gray-900 truncate">{channel.name}</h3>
        <div className="flex items-center gap-3 mt-1">
          <span className="text-sm text-gray-500">{channel.category || 'Uncategorized'}</span>
          {channel.region && (
            <span className="text-xs px-2 py-0.5 bg-blue-100 text-blue-700 rounded">{channel.region}</span>
          )}
          {channel.variant && (
            <span className="text-xs px-2 py-0.5 bg-purple-100 text-purple-700 rounded">{channel.variant}</span>
          )}
        </div>
      </div>

      {/* Stream Count Badge */}
      {hasMergedStreams && (
        <div className="flex items-center gap-2 px-3 py-2 bg-green-50 rounded-lg">
          <Layers className="w-4 h-4 text-green-600" />
          <span className="text-sm font-medium text-green-700">{channel.stream_count} streams</span>
        </div>
      )}

      <ChevronRight className="w-5 h-5 text-gray-400" />
    </div>
  );
}

// Channel Detail Side Panel
function ChannelDetailPanel({ channel, mergeDetails, onClose, onUpdate }) {
  const [showSplitDialog, setShowSplitDialog] = useState(false);
  const [selectedStreams, setSelectedStreams] = useState([]);

  const splitMutation = useMutation({
    mutationFn: async (streamIds) => {
      const response = await api.post(
        `/channels/${channel.id}/split`,
        { stream_ids: streamIds }
      );
      return response.data;
    },
    onSuccess: () => {
      setShowSplitDialog(false);
      setSelectedStreams([]);
      onUpdate();
      alert('Channel split successfully!');
    },
  });

  return (
    <div className="w-[600px] bg-white border-l border-gray-200 shadow-xl flex flex-col h-[calc(100vh-73px)] overflow-hidden">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div className="flex-1">
            <h2 className="text-2xl font-bold text-gray-900 mb-1">{channel.name}</h2>
            <p className="text-gray-600">{mergeDetails.total_streams} merged streams</p>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* Merge Methods Summary */}
        <div className="flex flex-wrap gap-2">
          {Object.entries(mergeDetails.merge_methods).map(([method, count]) => (
            <span
              key={method}
              className="px-3 py-1 bg-gray-100 text-gray-700 rounded-full text-sm"
            >
              {method}: {count}
            </span>
          ))}
        </div>
      </div>

      {/* Streams List */}
      <div className="flex-1 overflow-y-auto p-6">
        <div className="space-y-3">
          {mergeDetails.streams.map((stream, idx) => (
            <StreamCard
              key={stream.stream_id}
              stream={stream}
              rank={idx + 1}
              isSelected={selectedStreams.includes(stream.stream_id)}
              onSelect={(selected) => {
                if (selected) {
                  setSelectedStreams([...selectedStreams, stream.stream_id]);
                } else {
                  setSelectedStreams(selectedStreams.filter(id => id !== stream.stream_id));
                }
              }}
            />
          ))}
        </div>
      </div>

      {/* Actions */}
      <div className="p-6 border-t border-gray-200 bg-gray-50">
        {selectedStreams.length > 0 ? (
          <button
            onClick={() => setShowSplitDialog(true)}
            className="w-full flex items-center justify-center gap-2 px-6 py-3 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium transition-colors"
          >
            <Split className="w-5 h-5" />
            Split {selectedStreams.length} stream{selectedStreams.length > 1 ? 's' : ''} into new channel
          </button>
        ) : (
          <p className="text-center text-gray-500 text-sm">
            Select streams to split into a new channel
          </p>
        )}
      </div>

      {/* Split Confirmation Dialog */}
      {showSplitDialog && (
        <SplitDialog
          streamCount={selectedStreams.length}
          onConfirm={() => splitMutation.mutate(selectedStreams)}
          onCancel={() => setShowSplitDialog(false)}
          isLoading={splitMutation.isPending}
        />
      )}
    </div>
  );
}

// Stream Card in Detail Panel
function StreamCard({ stream, rank, isSelected, onSelect }) {
  const getRankColor = () => {
    if (rank === 1) return 'bg-yellow-100 text-yellow-800 border-yellow-300';
    if (rank === 2) return 'bg-gray-200 text-gray-800 border-gray-400';
    if (rank === 3) return 'bg-orange-100 text-orange-800 border-orange-300';
    return 'bg-gray-100 text-gray-700 border-gray-300';
  };

  const getConfidenceColor = (confidence) => {
    if (!confidence) return 'text-gray-500';
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 70) return 'text-yellow-600';
    return 'text-orange-600';
  };

  return (
    <div className={`border-2 rounded-lg p-4 transition-all ${
      isSelected ? 'border-blue-500 bg-blue-50' : 'border-gray-200 bg-white'
    }`}>
      <div className="flex items-start gap-3">
        {/* Selection Checkbox */}
        <input
          type="checkbox"
          checked={isSelected}
          onChange={(e) => onSelect(e.target.checked)}
          className="mt-1 w-4 h-4 text-blue-600 rounded focus:ring-2 focus:ring-blue-500"
        />

        <div className="flex-1">
          {/* Header */}
          <div className="flex items-start justify-between mb-2">
            <div className="flex items-center gap-2">
              <span className={`px-2 py-1 rounded border text-xs font-bold ${getRankColor()}`}>
                #{rank}
              </span>
              <span className="font-medium text-gray-900">{stream.original_name}</span>
            </div>
            {stream.quality_score && (
              <span className="text-sm font-semibold text-purple-600">
                {stream.quality_score} pts
              </span>
            )}
          </div>

          {/* Provider and Resolution */}
          <div className="flex items-center gap-3 mb-2">
            <span className="text-sm text-gray-600">
              <span className="font-medium">Provider:</span> {stream.provider_name}
            </span>
            {stream.resolution && (
              <span className="px-2 py-0.5 bg-blue-100 text-blue-700 rounded text-xs font-medium">
                {stream.resolution}
              </span>
            )}
          </div>

          {/* Merge Info */}
          <div className="flex items-center gap-2 text-sm">
            <span className="text-gray-600">
              <span className="font-medium">Method:</span> {stream.merge_method || 'unknown'}
            </span>
            {stream.merge_confidence && (
              <span className={`font-semibold ${getConfidenceColor(stream.merge_confidence)}`}>
                {stream.merge_confidence.toFixed(1)}% confidence
              </span>
            )}
          </div>

          {stream.merge_reason && (
            <p className="text-xs text-gray-500 mt-1 italic">
              {stream.merge_reason}
            </p>
          )}

          {/* Health Status */}
          {stream.consecutive_failures > 0 ? (
            <div className="flex items-center gap-1 mt-2 text-xs text-red-600">
              <AlertCircle className="w-3 h-3" />
              <span>{stream.consecutive_failures} failures</span>
            </div>
          ) : (
            <div className="flex items-center gap-1 mt-2 text-xs text-green-600">
              <CheckCircle className="w-3 h-3" />
              <span>Healthy</span>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

// Split Confirmation Dialog
function SplitDialog({ streamCount, onConfirm, onCancel, isLoading }) {
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl p-6 max-w-md w-full mx-4 shadow-2xl">
        <h3 className="text-xl font-bold text-gray-900 mb-4">Confirm Channel Split</h3>
        <p className="text-gray-600 mb-6">
          This will move {streamCount} stream{streamCount > 1 ? 's' : ''} into a new channel. 
          This action can be undone by manually merging the channels back together.
        </p>
        <div className="flex gap-3">
          <button
            onClick={onCancel}
            disabled={isLoading}
            className="flex-1 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 font-medium transition-colors"
          >
            Cancel
          </button>
          <button
            onClick={onConfirm}
            disabled={isLoading}
            className="flex-1 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 font-medium transition-colors disabled:opacity-50"
          >
            {isLoading ? 'Splitting...' : 'Split Channel'}
          </button>
        </div>
      </div>
    </div>
  );
}
