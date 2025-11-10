import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { AuthProvider } from './contexts/AuthContext'
import ProtectedRoute from './components/ProtectedRoute'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import Providers from './pages/Providers'
import Channels from './pages/Channels'
import VOD from './pages/VOD'
import Settings from './pages/Settings'
import SystemInfo from './pages/SystemInfo'
import Users from './pages/Users'
import Analytics from './pages/Analytics'
import Login from './pages/Login'

function App() {
  return (
    <Router>
        <AuthProvider>
          <Routes>
            <Route path="/login" element={<Login />} />
            <Route path="/*" element={
              <ProtectedRoute>
                <Layout>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/providers" element={<Providers />} />
                    <Route path="/channels" element={<Channels />} />
                    <Route path="/vod" element={<VOD />} />
                    <Route path="/settings" element={<Settings />} />
                    <Route path="/system" element={<SystemInfo />} />
                    <Route path="/users" element={<Users />} />
                    <Route path="/analytics" element={<Analytics />} />
                  </Routes>
                </Layout>
              </ProtectedRoute>
            } />
          </Routes>
        </AuthProvider>
      </Router>
  )
}

export default App
