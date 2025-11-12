import React, { useState, useEffect } from 'react';
import { Typography, Paper, Grid, Box, CircularProgress, Alert } from '@mui/material';
import { useAuth } from '../contexts/AuthContext';

function StatCard({ title, value, loading }) {
  return (
    <Paper sx={{ p: 2, textAlign: 'center', height: '100%' }}>
      <Typography variant="h6">{title}</Typography>
      <Typography variant="h3" sx={{ mt: 1 }}>
        {loading ? <CircularProgress size={40} /> : value}
      </Typography>
    </Paper>
  );
}

function DashboardPage() {
  const { api } = useAuth();
  const [stats, setStats] = useState({ providers: 0, channels: 0, vod: 0 });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        setLoading(true);
        // Assuming a single endpoint for stats. We can change this if needed.
        const response = await api.get('/system/stats'); 
        setStats(response.data);
        setError(null);
      } catch (err) {
        console.error("Failed to fetch dashboard stats:", err);
        setError("Could not load system statistics. The backend might be unavailable.");
        // Set default stats on error to avoid breaking the UI
        setStats({ providers: 'N/A', channels: 'N/A', vod: 'N/A' });
      } finally {
        setLoading(false);
      }
    };

    fetchStats();
  }, [api]);

  return (
    <Box>
      <Typography variant="h4" gutterBottom>
        Dashboard
      </Typography>
      {error && <Alert severity="error" sx={{ mb: 3 }}>{error}</Alert>}
      <Grid container spacing={3}>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="Providers" value={stats.providers} loading={loading} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="Channels" value={stats.channels} loading={loading} />
        </Grid>
        <Grid item xs={12} sm={6} md={4}>
          <StatCard title="VOD Items" value={stats.vod} loading={loading} />
        </Grid>
      </Grid>
    </Box>
  );
}

export default DashboardPage;
