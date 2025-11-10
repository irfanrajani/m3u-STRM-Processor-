import React, { useState } from 'react';
import './App.css';

function App() {
  const [m3uUrl, setM3uUrl] = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [mergeDuplicates, setMergeDuplicates] = useState(true);
  const [preferQuality, setPreferQuality] = useState('best');
  const [organizeByCategory, setOrganizeByCategory] = useState(false);
  const [fuzzyThreshold, setFuzzyThreshold] = useState(0.85);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [stats, setStats] = useState(null);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    setError('');
    setStats(null);
    setIsLoading(true);

    try {
      const response = await fetch('/process-m3u/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          m3u_url: m3uUrl,
          output_path: outputPath,
          merge_duplicates: mergeDuplicates,
          prefer_quality: preferQuality,
          organize_by_category: organizeByCategory,
          fuzzy_match_threshold: fuzzyThreshold,
        }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An unknown error occurred.');
      }

      setMessage(data.message);
      setStats({
        created: data.channels_created,
        removed: data.duplicates_removed || 0,
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🎬 M3U to STRM Processor</h1>
        <p className="subtitle">Smart IPTV Channel Converter</p>
        
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>
              M3U Playlist URL:
              <input
                type="text"
                value={m3uUrl}
                onChange={(e) => setM3uUrl(e.target.value)}
                placeholder="https://example.com/playlist.m3u"
                required
              />
            </label>
          </div>

          <div className="form-group">
            <label>
              Output Path:
              <input
                type="text"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
                placeholder="channels"
                required
              />
            </label>
          </div>

          <div className="options-section">
            <h3>Processing Options</h3>
            
            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={mergeDuplicates}
                  onChange={(e) => setMergeDuplicates(e.target.checked)}
                />
                Merge duplicate channels
              </label>
            </div>

            <div className="checkbox-group">
              <label>
                <input
                  type="checkbox"
                  checked={organizeByCategory}
                  onChange={(e) => setOrganizeByCategory(e.target.checked)}
                />
                Organize by category
              </label>
            </div>

            {mergeDuplicates && (
              <>
                <div className="form-group">
                  <label>
                    Quality Preference:
                    <select
                      value={preferQuality}
                      onChange={(e) => setPreferQuality(e.target.value)}
                    >
                      <option value="best">Best Available</option>
                      <option value="4k">4K Only</option>
                      <option value="hd">HD Only</option>
                      <option value="sd">SD Only</option>
                      <option value="all">Keep All Variants</option>
                    </select>
                  </label>
                </div>

                <div className="form-group">
                  <label>
                    Fuzzy Match Threshold: {fuzzyThreshold.toFixed(2)}
                    <input
                      type="range"
                      min="0.5"
                      max="1.0"
                      step="0.05"
                      value={fuzzyThreshold}
                      onChange={(e) => setFuzzyThreshold(parseFloat(e.target.value))}
                    />
                    <span className="range-hint">
                      (Lower = more aggressive merging)
                    </span>
                  </label>
                </div>
              </>
            )}
          </div>

          <button type="submit" disabled={isLoading} className="submit-btn">
            {isLoading ? 'Processing...' : '🚀 Create STRM Files'}
          </button>
        </form>

        {stats && (
          <div className="stats-box">
            <h3>✅ Processing Complete!</h3>
            <p>Created {stats.created} STRM files</p>
            {stats.removed > 0 && (
              <p>Merged/removed {stats.removed} duplicate channels</p>
            )}
          </div>
        )}

        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}

        <div className="help-section">
          <h4>💡 Tips:</h4>
          <ul>
            <li><strong>Merge duplicates:</strong> Combines channels like "ESPN", "ESPN HD", "ESPN 4K" into one</li>
            <li><strong>Quality preference:</strong> Choose which version to keep when merging</li>
            <li><strong>Organize by category:</strong> Creates subfolders like Sports/, News/, Movies/</li>
            <li><strong>Fuzzy matching:</strong> How similar channel names must be to merge (0.85 = 85% similar)</li>
          </ul>
        </div>
      </header>
    </div>
  );
}

export default App;
