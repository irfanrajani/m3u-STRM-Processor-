import React, { useState, useEffect } from 'react';
import axios from 'axios';

const Integration = () => {
  const [integrationData, setIntegrationData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [epgTest, setEpgTest] = useState(null);
  const [testingEpg, setTestingEpg] = useState(false);

  useEffect(() => {
    fetchIntegrationData();
  }, []);

  const fetchIntegrationData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/integration/urls', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setIntegrationData(response.data);
      setLoading(false);
    } catch (error) {
      console.error('Failed to fetch integration data:', error);
      setLoading(false);
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    // Show temporary success message
    const temp = document.createElement('div');
    temp.className = 'fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded shadow-lg z-50';
    temp.textContent = '✓ Copied to clipboard!';
    document.body.appendChild(temp);
    setTimeout(() => document.body.removeChild(temp), 2000);
  };

  const testEPG = async () => {
    setTestingEpg(true);
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/integration/test/epg', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setEpgTest(response.data);
    } catch (error) {
      setEpgTest({
        status: 'error',
        message: error.response?.data?.detail || 'Test failed'
      });
    }
    setTestingEpg(false);
  };

  const downloadEPG = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await axios.get('/api/integration/download/epg', {
        headers: { Authorization: `Bearer ${token}` },
        responseType: 'blob'
      });

      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', 'epg.xml');
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      alert('Failed to download EPG');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto">
      <h1 className="text-3xl font-bold text-gray-800 mb-2">Integration URLs</h1>
      <p className="text-gray-600 mb-6">
        Use these URLs to connect Plex, Emby, IPTV apps, and other clients
      </p>

      {/* EPG Test Section */}
      <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">📺 EPG Management</h2>

        <div className="flex gap-3 mb-4">
          <button
            onClick={testEPG}
            disabled={testingEpg}
            className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 disabled:bg-gray-400"
          >
            {testingEpg ? 'Testing...' : 'Test EPG Export'}
          </button>
          <button
            onClick={downloadEPG}
            className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700"
          >
            Download EPG (XML)
          </button>
        </div>

        {epgTest && (
          <div className={`p-4 rounded-lg border ${
            epgTest.status === 'success' ? 'bg-green-50 border-green-200' : 'bg-red-50 border-red-200'
          }`}>
            <p className={`font-semibold mb-2 ${
              epgTest.status === 'success' ? 'text-green-800' : 'text-red-800'
            }`}>
              {epgTest.status === 'success' ? '✓' : '✗'} {epgTest.message}
            </p>
            {epgTest.statistics && (
              <div className="text-sm text-gray-700 space-y-1">
                <p>• Channels with EPG: {epgTest.statistics.channels_with_epg}</p>
                <p>• Total Programs: {epgTest.statistics.total_programs}</p>
                <p>• Date Range: {epgTest.statistics.date_range_days} days</p>
                <p>• XMLTV Valid: {epgTest.valid_xmltv ? 'Yes' : 'No'}</p>
              </div>
            )}
          </div>
        )}
      </div>

      {/* HDHomeRun Section */}
      {integrationData?.hdhr && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            📡 {integrationData.hdhr.name}
          </h2>
          <p className="text-gray-600 mb-4">{integrationData.hdhr.description}</p>

          <div className="space-y-3 mb-6">
            {Object.entries(integrationData.hdhr.urls).map(([key, url]) => (
              <div key={key} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-700 capitalize">{key.replace('_', ' ')}</p>
                  <p className="font-mono text-sm text-gray-600 break-all">{url}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(url)}
                  className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 whitespace-nowrap"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {integrationData.hdhr.setup_instructions.plex && (
              <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg">
                <h3 className="font-semibold text-blue-800 mb-2">📺 Plex Setup</h3>
                <ol className="text-sm text-blue-700 space-y-1">
                  {integrationData.hdhr.setup_instructions.plex.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {integrationData.hdhr.setup_instructions.emby && (
              <div className="p-4 bg-purple-50 border border-purple-200 rounded-lg">
                <h3 className="font-semibold text-purple-800 mb-2">🎬 Emby Setup</h3>
                <ol className="text-sm text-purple-700 space-y-1">
                  {integrationData.hdhr.setup_instructions.emby.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Xtream Codes Section */}
      {integrationData?.xtream && (
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            📱 {integrationData.xtream.name}
          </h2>
          <p className="text-gray-600 mb-4">{integrationData.xtream.description}</p>

          <div className="mb-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
            <h3 className="font-semibold text-yellow-800 mb-2">🔑 Your Credentials</h3>
            <div className="space-y-2">
              <div className="flex items-center gap-2">
                <span className="text-sm text-yellow-700 w-24">Server:</span>
                <code className="flex-1 bg-white px-2 py-1 rounded border border-yellow-300 text-sm">
                  {integrationData.xtream.credentials.server_url}
                </code>
                <button
                  onClick={() => copyToClipboard(integrationData.xtream.credentials.server_url)}
                  className="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Copy
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-yellow-700 w-24">Username:</span>
                <code className="flex-1 bg-white px-2 py-1 rounded border border-yellow-300 text-sm">
                  {integrationData.xtream.credentials.username}
                </code>
                <button
                  onClick={() => copyToClipboard(integrationData.xtream.credentials.username)}
                  className="px-2 py-1 text-xs bg-yellow-600 text-white rounded hover:bg-yellow-700"
                >
                  Copy
                </button>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-sm text-yellow-700 w-24">Password:</span>
                <code className="flex-1 bg-white px-2 py-1 rounded border border-yellow-300 text-sm">
                  YOUR_PASSWORD
                </code>
              </div>
            </div>
          </div>

          <div className="space-y-3 mb-6">
            {Object.entries(integrationData.xtream.urls).map(([key, url]) => (
              <div key={key} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-700 capitalize">{key.replace('_', ' ')}</p>
                  <p className="font-mono text-xs text-gray-600 break-all">{url}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(url)}
                  className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 whitespace-nowrap"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>

          <div className="grid md:grid-cols-2 gap-4">
            {integrationData.xtream.setup_instructions.tivimate && (
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <h3 className="font-semibold text-green-800 mb-2">📱 TiviMate Setup</h3>
                <ol className="text-sm text-green-700 space-y-1">
                  {integrationData.xtream.setup_instructions.tivimate.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}

            {integrationData.xtream.setup_instructions.iptv_smarters && (
              <div className="p-4 bg-pink-50 border border-pink-200 rounded-lg">
                <h3 className="font-semibold text-pink-800 mb-2">📱 IPTV Smarters Setup</h3>
                <ol className="text-sm text-pink-700 space-y-1">
                  {integrationData.xtream.setup_instructions.iptv_smarters.map((step, i) => (
                    <li key={i}>{step}</li>
                  ))}
                </ol>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Direct URLs Section */}
      {integrationData?.direct_urls && (
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-800 mb-2">
            🔗 {integrationData.direct_urls.name}
          </h2>
          <p className="text-gray-600 mb-4">{integrationData.direct_urls.description}</p>

          <div className="space-y-3">
            {Object.entries(integrationData.direct_urls.urls).map(([key, url]) => (
              <div key={key} className="flex items-center gap-2 p-3 bg-gray-50 rounded-lg border border-gray-200">
                <div className="flex-1">
                  <p className="text-sm font-semibold text-gray-700 capitalize">{key.replace('_', ' ')}</p>
                  <p className="font-mono text-sm text-gray-600 break-all">{url}</p>
                </div>
                <button
                  onClick={() => copyToClipboard(url)}
                  className="px-3 py-1 text-sm bg-indigo-600 text-white rounded hover:bg-indigo-700 whitespace-nowrap"
                >
                  Copy
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Notes Section */}
      {integrationData?.notes && (
        <div className="mt-6 p-4 bg-gray-50 border border-gray-200 rounded-lg">
          <h3 className="font-semibold text-gray-800 mb-2">💡 Important Notes</h3>
          <ul className="text-sm text-gray-700 space-y-1">
            {integrationData.notes.map((note, i) => (
              <li key={i}>{note}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default Integration;
