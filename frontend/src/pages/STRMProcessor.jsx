import { useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { FileVideo, Download, FolderOpen, Settings2, Zap, CheckCircle2 } from 'lucide-react';
import toast from 'react-hot-toast';
import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('accessToken');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default function STRMProcessor() {
  const [formData, setFormData] = useState({
    m3u_url: '',
    output_path: 'channels',
    merge_duplicates: true,
    prefer_quality: 'best',
    organize_by_category: false,
    fuzzy_match_threshold: 0.85,
    clean_output_first: false,
  });

  const [result, setResult] = useState(null);

  const processMutation = useMutation({
    mutationFn: async (data) => {
      const response = await api.post('/strm/process-m3u/', data);
      return response.data;
    },
    onSuccess: (data) => {
      setResult(data);
      toast.success(data.message || 'STRM files created successfully!');
    },
    onError: (error) => {
      toast.error(error?.response?.data?.detail || 'Failed to process M3U');
    },
  });

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!formData.m3u_url.trim()) {
      toast.error('M3U URL is required');
      return;
    }
    setResult(null);
    processMutation.mutate(formData);
  };

  return (
    <div className="px-4 sm:px-6 lg:px-8 py-8 max-w-5xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold bg-gradient-to-r from-brand-600 to-accent-600 bg-clip-text text-transparent mb-2">
          STRM File Processor
        </h1>
        <p className="text-gray-600">
          Convert M3U playlists to STRM files with intelligent duplicate detection and quality merging
        </p>
      </div>

      {/* Main Form */}
      <div className="bg-white rounded-lg shadow-md p-6 mb-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* M3U URL */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              <FileVideo className="inline h-4 w-4 mr-1" />
              M3U Playlist URL *
            </label>
            <input
              type="url"
              required
              value={formData.m3u_url}
              onChange={(e) => setFormData({ ...formData, m3u_url: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              placeholder="https://example.com/playlist.m3u8"
            />
            <p className="mt-1 text-xs text-gray-500">
              URL to your IPTV provider's M3U playlist file
            </p>
          </div>

          {/* Output Path */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              <FolderOpen className="inline h-4 w-4 mr-1" />
              Output Directory
            </label>
            <input
              type="text"
              value={formData.output_path}
              onChange={(e) => setFormData({ ...formData, output_path: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
              placeholder="channels"
            />
            <p className="mt-1 text-xs text-gray-500">
              Subdirectory under /output where STRM files will be saved
            </p>
          </div>

          {/* Quality Preference */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              <Zap className="inline h-4 w-4 mr-1" />
              Quality Preference
            </label>
            <select
              value={formData.prefer_quality}
              onChange={(e) => setFormData({ ...formData, prefer_quality: e.target.value })}
              className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-brand-500 focus:border-transparent"
            >
              <option value="best">Best Available (Auto-select highest quality)</option>
              <option value="4k">4K/UHD Only</option>
              <option value="hd">HD Only (720p/1080p)</option>
              <option value="sd">SD Only</option>
              <option value="all">Keep All Quality Variants</option>
            </select>
          </div>

          {/* Fuzzy Match Threshold */}
          <div>
            <label className="block text-sm font-semibold text-gray-900 mb-2">
              <Settings2 className="inline h-4 w-4 mr-1" />
              Fuzzy Match Threshold: {formData.fuzzy_match_threshold.toFixed(2)}
            </label>
            <input
              type="range"
              min="0.5"
              max="1"
              step="0.05"
              value={formData.fuzzy_match_threshold}
              onChange={(e) => setFormData({ ...formData, fuzzy_match_threshold: parseFloat(e.target.value) })}
              className="w-full h-2 bg-gradient-to-r from-brand-200 to-accent-200 rounded-lg appearance-none cursor-pointer accent-brand-600"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Loose (0.5)</span>
              <span>Exact (1.0)</span>
            </div>
            <p className="mt-1 text-xs text-gray-500">
              Higher values require closer name matches to merge duplicates
            </p>
          </div>

          {/* Options Grid */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <label className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={formData.merge_duplicates}
                onChange={(e) => setFormData({ ...formData, merge_duplicates: e.target.checked })}
                className="w-5 h-5 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
              />
              <div>
                <div className="text-sm font-medium text-gray-900">Merge Duplicates</div>
                <div className="text-xs text-gray-500">Combine similar channels</div>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={formData.organize_by_category}
                onChange={(e) => setFormData({ ...formData, organize_by_category: e.target.checked })}
                className="w-5 h-5 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
              />
              <div>
                <div className="text-sm font-medium text-gray-900">Organize by Category</div>
                <div className="text-xs text-gray-500">Sort into folders</div>
              </div>
            </label>

            <label className="flex items-center space-x-3 p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-colors">
              <input
                type="checkbox"
                checked={formData.clean_output_first}
                onChange={(e) => setFormData({ ...formData, clean_output_first: e.target.checked })}
                className="w-5 h-5 text-brand-600 border-gray-300 rounded focus:ring-brand-500"
              />
              <div>
                <div className="text-sm font-medium text-gray-900">Clean Output First</div>
                <div className="text-xs text-gray-500">Delete existing files</div>
              </div>
            </label>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={processMutation.isPending}
            className="w-full inline-flex items-center justify-center px-6 py-3.5 border border-transparent rounded-lg shadow-sm text-base font-semibold text-white bg-gradient-to-r from-brand-600 to-accent-600 hover:from-brand-700 hover:to-accent-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 shadow-glow-brand"
          >
            {processMutation.isPending ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-3"></div>
                Processing M3U...
              </>
            ) : (
              <>
                <Download className="h-5 w-5 mr-2" />
                Create STRM Files
              </>
            )}
          </button>
        </form>
      </div>

      {/* Results */}
      {result && (
        <div className="bg-gradient-to-br from-green-50 to-emerald-50 border border-green-200 rounded-lg p-6 shadow-md">
          <div className="flex items-start space-x-3">
            <CheckCircle2 className="h-6 w-6 text-green-600 mt-0.5 flex-shrink-0" />
            <div className="flex-1">
              <h3 className="text-lg font-bold text-green-900 mb-3">Processing Complete!</h3>
              
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
                <div className="bg-white/60 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-700">{result.channels_created}</div>
                  <div className="text-xs text-gray-600">Files Created</div>
                </div>
                <div className="bg-white/60 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-700">{result.duplicates_removed || 0}</div>
                  <div className="text-xs text-gray-600">Duplicates Merged</div>
                </div>
                <div className="bg-white/60 rounded-lg p-3">
                  <div className="text-2xl font-bold text-green-700">{result.categories_used || 1}</div>
                  <div className="text-xs text-gray-600">Categories</div>
                </div>
                <div className="bg-white/60 rounded-lg p-3 col-span-2 md:col-span-1">
                  <div className="text-sm font-mono text-green-700 truncate">{result.output_dir}</div>
                  <div className="text-xs text-gray-600">Output Directory</div>
                </div>
              </div>

              <p className="text-sm text-green-800">
                Point your media server (Plex, Jellyfin, Emby) to <code className="bg-white/80 px-2 py-1 rounded">{result.output_dir}</code> to access your channels!
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Help Section */}
      <div className="mt-8 bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h3 className="text-lg font-bold text-blue-900 mb-3">How It Works</h3>
        <ul className="space-y-2 text-sm text-blue-800">
          <li className="flex items-start">
            <span className="inline-block w-6 h-6 rounded-full bg-blue-200 text-blue-900 font-bold text-center mr-2 flex-shrink-0">1</span>
            <span>Provide your M3U playlist URL from your IPTV provider</span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-6 h-6 rounded-full bg-blue-200 text-blue-900 font-bold text-center mr-2 flex-shrink-0">2</span>
            <span>Configure quality preference and merging options</span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-6 h-6 rounded-full bg-blue-200 text-blue-900 font-bold text-center mr-2 flex-shrink-0">3</span>
            <span>STRM files are created with intelligent duplicate removal (e.g., "ESPN", "ESPN HD", "ESPN 4K" become one file)</span>
          </li>
          <li className="flex items-start">
            <span className="inline-block w-6 h-6 rounded-full bg-blue-200 text-blue-900 font-bold text-center mr-2 flex-shrink-0">4</span>
            <span>Point your media server to the output directory to start watching!</span>
          </li>
        </ul>
      </div>
    </div>
  );
}
