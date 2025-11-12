import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { X, Play, Pause, Signal, AlertCircle, Check, ArrowUpDown, Settings, Link as LinkIcon } from 'lucide-react';
import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export default function ChannelDetailModal({ channel, onClose }) {
  const [activeStream, setActiveStream] = useState(null);
  const [testingStream, setTestingStream] = useState(null);
  const queryClient = useQueryClient();

  // Fetch all streams for this channel
  const { data: streams = [], isLoading } = useQuery({
    queryKey: ['channel-streams', channel.id],
    queryFn: async () => {
      const response = await axios.get(`${API_URL}/api/channels/${channel.id}/streams`);
      return response.data || [];
    },
  });

  // Mutation to test stream health
  const testStreamMutation = useMutation({
    mutationFn: async (streamId) => {
      setTestingStream(streamId);
      const response = await axios.post(`${API_URL}/api/channels/streams/${streamId}/test`);
      return response.data;
    },
    onSuccess: (data, streamId) => {
      setTestingStream(null);
      queryClient.invalidateQueries(['channel-streams', channel.id]);
    },
    onError: (error, streamId) => {
      setTestingStream(null);
      console.error('Stream test failed:', error);
    },
  });

  // Mutation to update stream priority
  const updatePriorityMutation = useMutation({
    mutationFn: async ({ streamId, newPriority }) => {
      const response = await axios.patch(`${API_URL}/api/channels/streams/${streamId}`, {
        priority_order: newPriority,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['channel-streams', channel.id]);
    },
  });

  // Mutation to toggle stream active status
  const toggleStreamMutation = useMutation({
    mutationFn: async (streamId) => {
      const stream = streams.find(s => s.id === streamId);
      const response = await axios.patch(`${API_URL}/api/channels/streams/${streamId}`, {
        is_active: !stream.is_active,
      });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries(['channel-streams', channel.id]);
    },
  });

  const getQualityColor = (score) => {
    if (score >= 80) return 'text-green-600 bg-green-50';
    if (score >= 60) return 'text-blue-600 bg-blue-50';
    if (score >= 40) return 'text-yellow-600 bg-yellow-50';
    return 'text-red-600 bg-red-50';
  };

  const getResolutionBadge = (resolution) => {
    if (!resolution) return <span className="text-xs text-gray-400">Unknown</span>;
    
    const res = resolution.toLowerCase();
    if (res.includes('3840') || res.includes('4k')) {
      return <span className="px-2 py-0.5 text-xs font-semibold bg-purple-100 text-purple-800 rounded">4K UHD</span>;
    }
    if (res.includes('1920') || res.includes('1080')) {
      return <span className="px-2 py-0.5 text-xs font-semibold bg-blue-100 text-blue-800 rounded">FHD 1080p</span>;
    }
    if (res.includes('1280') || res.includes('720')) {
      return <span className="px-2 py-0.5 text-xs font-semibold bg-green-100 text-green-800 rounded">HD 720p</span>;
    }
    return <span className="px-2 py-0.5 text-xs font-semibold bg-gray-100 text-gray-800 rounded">SD</span>;
  };

  const formatBitrate = (bitrate) => {
    if (!bitrate) return 'N/A';
    if (bitrate >= 1000000) {
      return `${(bitrate / 1000000).toFixed(1)} Mbps`;
    }
    return `${(bitrate / 1000).toFixed(0)} Kbps`;
  };

  const sortedStreams = [...streams].sort((a, b) => {
    // Primary sort by priority order
    if (a.priority_order !== b.priority_order) {
      return (a.priority_order || 999) - (b.priority_order || 999);
    }
    // Secondary sort by quality score
    return (b.quality_score || 0) - (a.quality_score || 0);
  });

  const movePriority = (streamId, direction) => {
    const currentIndex = sortedStreams.findIndex(s => s.id === streamId);
    if (currentIndex === -1) return;

    const newIndex = direction === 'up' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= sortedStreams.length) return;

    // Swap priorities
    const currentPriority = sortedStreams[currentIndex].priority_order || currentIndex;
    const newPriority = sortedStreams[newIndex].priority_order || newIndex;

    updatePriorityMutation.mutate({ streamId, newPriority });
    updatePriorityMutation.mutate({ 
      streamId: sortedStreams[newIndex].id, 
      newPriority: currentPriority 
    });
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-5xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 flex items-center justify-between">
          <div className="flex items-center space-x-4">
            {channel.logo_url && (
              <img 
                src={channel.logo_url} 
                alt={channel.name}
                className="h-12 w-12 object-contain rounded"
              />
            )}
            <div>
              <h2 className="text-2xl font-bold text-gray-900">{channel.name}</h2>
              <div className="flex items-center space-x-3 text-sm text-gray-600 mt-1">
                <span>{channel.category || 'Uncategorized'}</span>
                {channel.region && (
                  <>
                    <span>•</span>
                    <span>{channel.region}</span>
                  </>
                )}
                {channel.variant && (
                  <>
                    <span>•</span>
                    <span className="font-semibold">{channel.variant}</span>
                  </>
                )}
              </div>
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 transition-colors"
          >
            <X className="h-6 w-6" />
          </button>
        </div>

        {/* Content */}
        <div className="flex-1 overflow-y-auto p-6">
          {isLoading ? (
            <div className="flex items-center justify-center h-64">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-brand-600"></div>
            </div>
          ) : streams.length === 0 ? (
            <div className="text-center py-12">
              <AlertCircle className="h-12 w-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-600">No streams found for this channel</p>
            </div>
          ) : (
            <div className="space-y-3">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-gray-900">
                  {streams.length} Stream{streams.length !== 1 ? 's' : ''} Available
                </h3>
                <p className="text-sm text-gray-600">
                  Streams are automatically ranked by quality
                </p>
              </div>

              {sortedStreams.map((stream, index) => (
                <div
                  key={stream.id}
                  className={`bg-gray-50 rounded-lg p-4 border-2 transition-all ${
                    stream.is_active 
                      ? 'border-green-200 hover:border-green-300' 
                      : 'border-gray-200 opacity-60'
                  }`}
                >
                  <div className="flex items-start justify-between">
                    <div className="flex-1 space-y-3">
                      {/* Stream Header */}
                      <div className="flex items-center space-x-3">
                        <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                          index === 0 ? 'bg-gradient-to-r from-yellow-400 to-yellow-600 text-white' :
                          index === 1 ? 'bg-gradient-to-r from-gray-300 to-gray-400 text-gray-800' :
                          index === 2 ? 'bg-gradient-to-r from-orange-400 to-orange-600 text-white' :
                          'bg-gray-200 text-gray-700'
                        }`}>
                          #{index + 1}
                        </div>
                        {getResolutionBadge(stream.resolution)}
                        <span className={`px-3 py-1 rounded-full text-xs font-semibold ${getQualityColor(stream.quality_score || 0)}`}>
                          <Signal className="inline h-3 w-3 mr-1" />
                          Quality: {stream.quality_score || 0}/100
                        </span>
                        {stream.is_active ? (
                          <span className="px-2 py-0.5 bg-green-100 text-green-800 text-xs font-semibold rounded-full">
                            Active
                          </span>
                        ) : (
                          <span className="px-2 py-0.5 bg-red-100 text-red-800 text-xs font-semibold rounded-full">
                            Disabled
                          </span>
                        )}
                      </div>

                      {/* Stream Details */}
                      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <span className="text-gray-500 font-medium">Provider:</span>
                          <p className="text-gray-900 mt-1">{stream.provider_name || 'Unknown'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 font-medium">Bitrate:</span>
                          <p className="text-gray-900 mt-1">{formatBitrate(stream.bitrate)}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 font-medium">Codec:</span>
                          <p className="text-gray-900 mt-1 uppercase">{stream.codec || 'N/A'}</p>
                        </div>
                        <div>
                          <span className="text-gray-500 font-medium">Format:</span>
                          <p className="text-gray-900 mt-1 uppercase">{stream.stream_format || 'N/A'}</p>
                        </div>
                      </div>

                      {/* Stream URL */}
                      <div className="bg-white rounded p-2 border border-gray-200">
                        <div className="flex items-center space-x-2 text-xs">
                          <LinkIcon className="h-3 w-3 text-gray-400" />
                          <code className="text-gray-600 truncate flex-1">
                            {stream.stream_url}
                          </code>
                        </div>
                      </div>

                      {/* Health Status */}
                      {stream.last_check && (
                        <div className="flex items-center space-x-2 text-xs text-gray-600">
                          {stream.consecutive_failures > 0 ? (
                            <>
                              <AlertCircle className="h-3 w-3 text-red-600" />
                              <span>Failed {stream.consecutive_failures} time(s)</span>
                              {stream.failure_reason && (
                                <span className="px-2 py-0.5 rounded bg-red-100 text-red-800">
                                  {stream.failure_reason}
                                </span>
                              )}
                            </>
                          ) : (
                            <>
                              <Check className="h-3 w-3 text-green-600" />
                              <span>Last checked: {new Date(stream.last_check).toLocaleString()}</span>
                              <span className="px-2 py-0.5 rounded bg-green-100 text-green-800">
                                healthy
                              </span>
                            </>
                          )}
                        </div>
                      )}
                    </div>

                    {/* Actions */}
                    <div className="flex flex-col space-y-2 ml-4">
                      <button
                        onClick={() => testStreamMutation.mutate(stream.id)}
                        disabled={testingStream === stream.id}
                        className="px-3 py-2 bg-brand-600 text-white rounded-lg hover:bg-brand-700 disabled:opacity-50 text-sm font-medium flex items-center space-x-1"
                      >
                        {testingStream === stream.id ? (
                          <>
                            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                            <span>Testing...</span>
                          </>
                        ) : (
                          <>
                            <Play className="h-4 w-4" />
                            <span>Test</span>
                          </>
                        )}
                      </button>

                      <button
                        onClick={() => toggleStreamMutation.mutate(stream.id)}
                        className={`px-3 py-2 rounded-lg text-sm font-medium ${
                          stream.is_active
                            ? 'bg-red-100 text-red-700 hover:bg-red-200'
                            : 'bg-green-100 text-green-700 hover:bg-green-200'
                        }`}
                      >
                        {stream.is_active ? 'Disable' : 'Enable'}
                      </button>

                      <div className="flex space-x-1">
                        <button
                          onClick={() => movePriority(stream.id, 'up')}
                          disabled={index === 0}
                          className="px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-30 text-xs"
                          title="Move up"
                        >
                          ↑
                        </button>
                        <button
                          onClick={() => movePriority(stream.id, 'down')}
                          disabled={index === sortedStreams.length - 1}
                          className="px-2 py-1 bg-gray-200 text-gray-700 rounded hover:bg-gray-300 disabled:opacity-30 text-xs"
                          title="Move down"
                        >
                          ↓
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="px-6 py-4 border-t border-gray-200 bg-gray-50 flex items-center justify-between">
          <div className="text-sm text-gray-600">
            <p>Streams are automatically ranked by quality score and can be manually reordered</p>
          </div>
          <button
            onClick={onClose}
            className="px-4 py-2 bg-gray-200 text-gray-800 rounded-lg hover:bg-gray-300 font-medium"
          >
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
