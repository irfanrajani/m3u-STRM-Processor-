import React, { useState } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import { useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import MainLayout from './components/MainLayout';
import DashboardPage from './pages/DashboardEnhanced';
import Providers from './pages/Providers';
import Settings from './pages/SettingsEnhanced';
import VOD from './pages/VOD';
import Channels from './pages/Channels';
import ChannelsNew from './pages/Channels_New';
import STRMProcessor from './pages/STRMProcessor';
import Analytics from './pages/Analytics';
import Favorites from './pages/Favorites';
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

  // A wrapper for routes that require authentication
  function PrivateRoute({ children }) {
    const { isAuthenticated, isLoading } = useAuth();
    if (isLoading) {
      return <div>Loading...</div>; // Or a spinner component
    }
    return isAuthenticated ? children : <Navigate to="/login" />;
  }

  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route
        path="/*"
        element={
          <PrivateRoute>
            <MainLayout>
              <Routes>
                <Route path="/dashboard" element={<DashboardPage />} />
                <Route path="/strm-processor" element={<STRMProcessor />} />
                <Route path="/providers" element={<Providers />} />
                <Route path="/channels" element={<ChannelsNew />} />
                <Route path="/channels-old" element={<Channels />} />
                <Route path="/vod" element={<VOD />} />
                <Route path="/favorites" element={<Favorites />} />
                <Route path="/analytics" element={<Analytics />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/" element={<Navigate to="/dashboard" />} />
              </Routes>
            </MainLayout>
          </PrivateRoute>
        }
      />
    </Routes>
  );
}

export default App;
