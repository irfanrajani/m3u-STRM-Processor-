import React, { useState } from 'react';
import './App.css';

function App() {
  const [m3uUrl, setM3uUrl] = useState('');
  const [outputPath, setOutputPath] = useState('');
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (event) => {
    event.preventDefault();
    setMessage('');
    setError('');
    setIsLoading(true);

    try {
      const response = await fetch('/process-m3u/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ m3u_url: m3uUrl, output_path: outputPath }),
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'An unknown error occurred.');
      }

      setMessage(data.message);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>IPTV Stream Manager</h1>
        <form onSubmit={handleSubmit}>
          <div>
            <label>
              M3U URL:
              <input
                type="text"
                value={m3uUrl}
                onChange={(e) => setM3uUrl(e.target.value)}
                required
              />
            </label>
          </div>
          <div>
            <label>
              Output Path:
              <input
                type="text"
                value={outputPath}
                onChange={(e) => setOutputPath(e.target.value)}
                required
              />
            </label>
          </div>
          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Processing...' : 'Create STRM Files'}
          </button>
        </form>
        {message && <p className="success-message">{message}</p>}
        {error && <p className="error-message">{error}</p>}
      </header>
    </div>
  );
}

export default App;
