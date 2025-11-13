import { useState, useEffect, useRef } from 'react';
import { Activity, CheckCircle, XCircle, AlertTriangle, Radio, Zap } from 'lucide-react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';
const WS_URL = API_URL.replace('http', 'ws');

export default function RealTimeMonitor() {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [stats, setStats] = useState({
    healthChecks: 0,
    failovers: 0,
    syncProgress: {}
  });
  const ws = useRef(null);
  const reconnectTimeout = useRef(null);

  useEffect(() => {
    connectWebSocket();

    return () => {
      if (ws.current) {
        ws.current.close();
      }
      if (reconnectTimeout.current) {
        clearTimeout(reconnectTimeout.current);
      }
    };
  }, []);

  const connectWebSocket = () => {
    try {
      ws.current = new WebSocket(`${WS_URL}/api/ws/monitor`);

      ws.current.onopen = () => {
        console.log('WebSocket connected');
        setConnected(true);
        // Send ping every 30 seconds
        const pingInterval = setInterval(() => {
          if (ws.current && ws.current.readyState === WebSocket.OPEN) {
            ws.current.send(JSON.stringify({ type: 'ping' }));
          }
        }, 30000);

        ws.current.pingInterval = pingInterval;
      };

      ws.current.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          handleMessage(data);
        } catch (err) {
          console.error('Failed to parse WebSocket message:', err);
        }
      };

      ws.current.onerror = (error) => {
        console.error('WebSocket error:', error);
      };

      ws.current.onclose = () => {
        console.log('WebSocket disconnected');
        setConnected(false);
        if (ws.current.pingInterval) {
          clearInterval(ws.current.pingInterval);
        }

        // Reconnect after 5 seconds
        reconnectTimeout.current = setTimeout(() => {
          console.log('Attempting to reconnect...');
          connectWebSocket();
        }, 5000);
      };
    } catch (err) {
      console.error('Failed to connect WebSocket:', err);
      setConnected(false);
    }
  };

  const handleMessage = (data) => {
    const { type, data: payload, timestamp } = data;

    // Add to events feed
    const event = {
      id: Date.now() + Math.random(),
      type,
      payload,
      timestamp: new Date(timestamp).toLocaleTimeString()
    };

    setEvents(prev => [event, ...prev].slice(0, 50)); // Keep last 50 events

    // Update stats
    switch (type) {
      case 'health_check_update':
        setStats(prev => ({
          ...prev,
          healthChecks: prev.healthChecks + 1
        }));
        break;

      case 'stream_failover':
        setStats(prev => ({
          ...prev,
          failovers: prev.failovers + 1
        }));
        break;

      case 'sync_progress':
        setStats(prev => ({
          ...prev,
          syncProgress: {
            ...prev.syncProgress,
            [payload.provider_id]: {
              name: payload.provider_name,
              progress: payload.progress,
              total: payload.total,
              percentage: payload.percentage,
              status: payload.status
            }
          }
        }));
        break;

      default:
        break;
    }
  };

  const getEventIcon = (type) => {
    switch (type) {
      case 'health_check_update':
        return <Activity className="h-4 w-4 text-blue-500" />;
      case 'stream_failover':
        return <Zap className="h-4 w-4 text-yellow-500" />;
      case 'sync_progress':
        return <Radio className="h-4 w-4 text-green-500" />;
      case 'alert':
        return <AlertTriangle className="h-4 w-4 text-red-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEventColor = (type) => {
    switch (type) {
      case 'health_check_update':
        return 'bg-blue-50 border-blue-200';
      case 'stream_failover':
        return 'bg-yellow-50 border-yellow-200';
      case 'sync_progress':
        return 'bg-green-50 border-green-200';
      case 'alert':
        return 'bg-red-50 border-red-200';
      default:
        return 'bg-gray-50 border-gray-200';
    }
  };

  const renderEventContent = (event) => {
    const { type, payload } = event;

    switch (type) {
      case 'health_check_update':
        return (
          <div className="flex items-center justify-between">
            <span className="font-medium">{payload.channel_name}</span>
            <span className={`text-sm ${payload.is_alive ? 'text-green-600' : 'text-red-600'}`}>
              {payload.is_alive ? 'Alive' : 'Dead'}
            </span>
          </div>
        );

      case 'stream_failover':
        return (
          <div>
            <div className="font-medium">{payload.channel_name}</div>
            <div className="text-xs text-gray-600 mt-1">{payload.reason}</div>
          </div>
        );

      case 'sync_progress':
        return (
          <div>
            <div className="font-medium">{payload.provider_name}</div>
            <div className="flex items-center space-x-2 mt-1">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-green-500 h-2 rounded-full transition-all"
                  style={{ width: `${payload.percentage}%` }}
                />
              </div>
              <span className="text-xs text-gray-600">{payload.percentage}%</span>
            </div>
          </div>
        );

      case 'alert':
        return (
          <div>
            <div className="font-medium">{payload.title}</div>
            <div className="text-sm text-gray-600 mt-1">{payload.message}</div>
          </div>
        );

      case 'vod_generation_progress':
        return (
          <div>
            <div className="font-medium">VOD STRM Generation</div>
            <div className="flex items-center space-x-2 mt-1">
              <div className="flex-1 bg-gray-200 rounded-full h-2">
                <div
                  className="bg-purple-500 h-2 rounded-full transition-all"
                  style={{ width: `${payload.percentage}%` }}
                />
              </div>
              <span className="text-xs text-gray-600">{payload.percentage}%</span>
            </div>
          </div>
        );

      default:
        return <div className="text-sm text-gray-600">Unknown event type</div>;
    }
  };

  return (
    <div className="bg-white rounded-xl shadow-lg overflow-hidden">
      {/* Header */}
      <div className="bg-gradient-to-r from-brand-600 to-accent-600 px-6 py-4 flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <Activity className="h-6 w-6 text-white" />
          <h2 className="text-xl font-bold text-white">Real-Time Activity</h2>
        </div>
        <div className="flex items-center space-x-2">
          <div className={`h-2 w-2 rounded-full ${connected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`} />
          <span className="text-sm text-white">{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4 p-6 border-b border-gray-200">
        <div className="text-center">
          <div className="text-2xl font-bold text-brand-600">{stats.healthChecks}</div>
          <div className="text-xs text-gray-600">Health Checks</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-yellow-600">{stats.failovers}</div>
          <div className="text-xs text-gray-600">Failovers</div>
        </div>
        <div className="text-center">
          <div className="text-2xl font-bold text-green-600">
            {Object.keys(stats.syncProgress).length}
          </div>
          <div className="text-xs text-gray-600">Active Syncs</div>
        </div>
      </div>

      {/* Active Syncs */}
      {Object.keys(stats.syncProgress).length > 0 && (
        <div className="p-6 border-b border-gray-200">
          <h3 className="text-sm font-semibold text-gray-900 mb-3">Active Syncs</h3>
          <div className="space-y-2">
            {Object.values(stats.syncProgress).map((sync, idx) => (
              <div key={idx} className="bg-green-50 p-3 rounded-lg">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-sm font-medium">{sync.name}</span>
                  <span className="text-xs text-gray-600">{sync.percentage}%</span>
                </div>
                <div className="bg-gray-200 rounded-full h-2">
                  <div
                    className="bg-green-500 h-2 rounded-full transition-all"
                    style={{ width: `${sync.percentage}%` }}
                  />
                </div>
                <div className="text-xs text-gray-600 mt-1">{sync.status}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Event Feed */}
      <div className="p-6">
        <h3 className="text-sm font-semibold text-gray-900 mb-3">Recent Events</h3>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {events.length === 0 ? (
            <div className="text-center py-8 text-gray-500">
              <Activity className="h-8 w-8 mx-auto mb-2 opacity-50" />
              <p className="text-sm">No events yet. Waiting for activity...</p>
            </div>
          ) : (
            events.map(event => (
              <div
                key={event.id}
                className={`p-3 rounded-lg border ${getEventColor(event.type)} transition-all hover:shadow-md`}
              >
                <div className="flex items-start space-x-3">
                  <div className="flex-shrink-0 mt-0.5">
                    {getEventIcon(event.type)}
                  </div>
                  <div className="flex-1 min-w-0">
                    {renderEventContent(event)}
                  </div>
                  <div className="flex-shrink-0 text-xs text-gray-500">
                    {event.timestamp}
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
