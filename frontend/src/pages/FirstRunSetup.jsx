import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import axios from 'axios';

const FirstRunSetup = () => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [setupComplete, setSetupComplete] = useState(false);
  const [step, setStep] = useState(1);
  const [formData, setFormData] = useState({
    admin_username: 'admin',
    admin_email: 'admin@localhost',
    admin_password: ''
  });
  const [generatedPassword, setGeneratedPassword] = useState('');
  const [credentials, setCredentials] = useState(null);
  const [error, setError] = useState('');

  useEffect(() => {
    checkSetupStatus();
  }, []);

  const checkSetupStatus = async () => {
    try {
      const response = await axios.get('/api/setup/status');
      if (response.data.setup_complete) {
        setSetupComplete(true);
        // Redirect to login after 2 seconds
        setTimeout(() => navigate('/login'), 2000);
      }
      setLoading(false);
    } catch (error) {
      console.error('Failed to check setup status:', error);
      setLoading(false);
    }
  };

  const generatePassword = () => {
    const chars = 'ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnpqrstuvwxyz23456789!@#$%^&*';
    let password = '';
    for (let i = 0; i < 16; i++) {
      password += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    setGeneratedPassword(password);
    setFormData({ ...formData, admin_password: password });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    if (!formData.admin_password) {
      setError('Please set a password or generate one');
      return;
    }

    try {
      const response = await axios.post('/api/setup/initialize', formData);
      setCredentials(response.data.credentials);
      setStep(2);
    } catch (error) {
      setError(error.response?.data?.detail || 'Setup failed');
    }
  };

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text);
    alert('Copied to clipboard!');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Checking setup status...</p>
        </div>
      </div>
    );
  }

  if (setupComplete) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-green-50 to-emerald-100 flex items-center justify-center">
        <div className="bg-white p-8 rounded-lg shadow-lg text-center max-w-md">
          <div className="text-green-500 text-6xl mb-4">✓</div>
          <h2 className="text-2xl font-bold text-gray-800 mb-2">Setup Complete!</h2>
          <p className="text-gray-600">Redirecting to login...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-xl max-w-2xl w-full p-8">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-2">
            🎬 M3U STRM Processor
          </h1>
          <p className="text-gray-600">First-Run Setup Wizard</p>
        </div>

        {step === 1 && (
          <>
            <h2 className="text-2xl font-semibold text-gray-800 mb-6">
              Create Admin Account
            </h2>

            {error && (
              <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded mb-4">
                {error}
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Username
                </label>
                <input
                  type="text"
                  value={formData.admin_username}
                  onChange={(e) => setFormData({ ...formData, admin_username: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Email
                </label>
                <input
                  type="email"
                  value={formData.admin_email}
                  onChange={(e) => setFormData({ ...formData, admin_email: e.target.value })}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Password
                </label>
                <div className="flex gap-2">
                  <input
                    type="text"
                    value={formData.admin_password}
                    onChange={(e) => setFormData({ ...formData, admin_password: e.target.value })}
                    placeholder="Enter password or generate one"
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-500"
                    required
                  />
                  <button
                    type="button"
                    onClick={generatePassword}
                    className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 whitespace-nowrap"
                  >
                    Generate
                  </button>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  💡 Recommended: Use the generate button for a secure password
                </p>
              </div>

              <button
                type="submit"
                className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 font-semibold text-lg transition"
              >
                Complete Setup
              </button>
            </form>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">ℹ️ What's Next?</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>• Your credentials will be displayed only once</li>
                <li>• Save them in a secure password manager</li>
                <li>• You'll be redirected to login after setup</li>
              </ul>
            </div>
          </>
        )}

        {step === 2 && credentials && (
          <>
            <div className="text-center mb-6">
              <div className="text-green-500 text-6xl mb-4">✓</div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">
                Setup Complete!
              </h2>
              <p className="text-gray-600">Save these credentials now</p>
            </div>

            <div className="bg-yellow-50 border-2 border-yellow-400 rounded-lg p-6 mb-6">
              <p className="text-yellow-800 font-bold mb-4 text-center">
                ⚠️ IMPORTANT: Save these credentials!
              </p>
              <p className="text-yellow-700 text-sm text-center mb-4">
                This is the ONLY time your password will be displayed.
              </p>

              <div className="space-y-3">
                <div className="bg-white p-4 rounded border border-gray-300">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-gray-600">Username</p>
                      <p className="font-mono font-bold text-lg">{credentials.username}</p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(credentials.username)}
                      className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                    >
                      Copy
                    </button>
                  </div>
                </div>

                <div className="bg-white p-4 rounded border border-gray-300">
                  <div className="flex justify-between items-center">
                    <div className="flex-1 pr-4">
                      <p className="text-sm text-gray-600">Password</p>
                      <p className="font-mono font-bold text-lg break-all">{credentials.password}</p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(credentials.password)}
                      className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded whitespace-nowrap"
                    >
                      Copy
                    </button>
                  </div>
                </div>

                <div className="bg-white p-4 rounded border border-gray-300">
                  <div className="flex justify-between items-center">
                    <div>
                      <p className="text-sm text-gray-600">Email</p>
                      <p className="font-mono text-lg">{credentials.email}</p>
                    </div>
                    <button
                      onClick={() => copyToClipboard(credentials.email)}
                      className="px-3 py-1 text-sm bg-gray-100 hover:bg-gray-200 rounded"
                    >
                      Copy
                    </button>
                  </div>
                </div>
              </div>
            </div>

            <button
              onClick={() => navigate('/login')}
              className="w-full bg-indigo-600 text-white py-3 px-6 rounded-lg hover:bg-indigo-700 font-semibold text-lg transition"
            >
              Continue to Login
            </button>

            <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
              <h3 className="font-semibold text-blue-800 mb-2">📝 Recommended Next Steps</h3>
              <ul className="text-sm text-blue-700 space-y-1">
                <li>1. Save these credentials in your password manager</li>
                <li>2. Login with your new account</li>
                <li>3. Add your IPTV providers in Settings</li>
                <li>4. Configure integrations (Plex, Emby, etc.)</li>
              </ul>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default FirstRunSetup;
