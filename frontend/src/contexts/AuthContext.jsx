import React, { createContext, useState, useContext, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext({
  user: null,
  isAuthenticated: false,
  isAdmin: false,
  isLoading: true,
  login: () => {},
  logout: () => {},
  api: null
});

const api = axios.create({
  baseURL: '/api',
});

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isAdmin, setIsAdmin] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('accessToken');
    if (token) {
      api.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      
      // Fetch user data to determine role
      api.get('/auth/me')
        .then(response => {
          setUser(response.data);
          setIsAuthenticated(true);
          setIsAdmin(response.data.role === 'admin');
        })
        .catch(error => {
          console.error('Failed to fetch user data:', error);
          localStorage.removeItem('accessToken');
          setIsAuthenticated(false);
          setIsAdmin(false);
        })
        .finally(() => {
          setIsLoading(false);
        });
    } else {
      setIsLoading(false);
    }
  }, []);

  const login = async (username, password) => {
    try {
      const formData = new URLSearchParams();
      formData.append('username', username);
      formData.append('password', password);

      const response = await api.post('/auth/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      
      const { access_token } = response.data;
      localStorage.setItem('accessToken', access_token);
      api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`;
      
      // Fetch user data to set role
      const userResponse = await api.get('/auth/me');
      setUser(userResponse.data);
      setIsAuthenticated(true);
      setIsAdmin(userResponse.data.role === 'admin');
      
      return true;
    } catch (error) {
      console.error('Login failed:', error);
      return false;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    delete api.defaults.headers.common['Authorization'];
    setUser(null);
    setIsAuthenticated(false);
    setIsAdmin(false);
  };

  return (
    <AuthContext.Provider value={{ user, isAuthenticated, isAdmin, isLoading, login, logout, api }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);
