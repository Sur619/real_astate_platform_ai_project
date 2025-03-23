`
import React, { createContext, useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { jwtDecode } from 'jwt-decode';


export const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [token, setToken] = useState(localStorage.getItem('token') || null);
  const [userInfo, setUserInfo] = useState(null);
  const baseUrl = "http://0.0.0.0:8000";

  const isTokenExpired = (token) => {
    if (!token) return true;
    try {
      const decoded = jwtDecode(token);
      return decoded.exp < Date.now() / 1000;
    } catch (error) {
      return true;
    }
  };

  const refreshAccessToken = async () => {
    try {
      const response = await fetch(`${baseUrl} / users / refresh / `, {
        method: 'POST',
        credentials: 'include',
        headers: {
          Authorization: Bearer ${token},
        },
      });

      if (response.status === 401) {
        console.error('Unauthorized: Refresh token is invalid or expired.');
        logout();
        return null;
      }

      const data = await response.json();
      console.log('refreshAccessToken: ', data);
      setToken(data.access_token);
      localStorage.setItem('token', data.access_token);
      return data.access_token;
    } catch (error) {
      console.error('Error refreshing token:', error);
      logout();
      return null;
    }
  };

  const fetchUserInfo = async () => {
    const accessToken = localStorage.getItem('token');
    if (!accessToken) return;
    try {
      const response = await fetch(`${baseUrl} / users / get / me / `, {
        method: 'GET',
        headers: {
          Authorization: Bearer ${accessToken},
        },
      });

      if (response.status === 401) {
        console.log("Access token expired, trying to refresh...");
        const newAccessToken = await refreshAccessToken();
        if (newAccessToken) {
          return fetchUserInfo(newAccessToken);
        }
        return;
      }

      if (!response.ok) throw new Error('Failed to fetch user info');

      const data = await response.json();
      setUserInfo({
        username: data.username,
        firstname: data.firstname,
        lastname: data.lastname,
        email: data.email
      });
    } catch (error) {
      console.error('Error fetching user info:', error);
    }
  };

  const login = async (formData) => {
    try {
      const response = await fetch(`${baseUrl} / users / login / `, {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: formData,
        credentials: 'include',
      });

      const data = await response.json();

      if (response.ok) {
        setToken(data.access_token);
        localStorage.setItem('token', data.access_token);
        fetchUserInfo(data.access_token);
        return { success: true };
      } else {
        if (response.status === 403 && data.detail === 'Email not verified') {
          return { success: false, message: Email not verified. A verification email has been sent to ${data.email}., status: 403 };
        }
        return { success: false, message: data.detail, status: response.status };
      }
    } catch (error) {
      return { success: false, message: 'Login failed.', status: 500 };
    }
  };

  const logout = async () => {
    const accessToken = localStorage.getItem('token');
    try {
        const response = await fetch(`${baseUrl} / users / logout / `, {
            method: 'POST',
            credentials: 'include',
            headers: {
            Authorization: Bearer ${accessToken},
           },
        });

        if (!response.ok) {
            throw new Error(`
logout
error: ${response.status} ${response.statusText}`);
        }
    } catch (error) {
        console.error("logout error:", error);
    } finally {
        localStorage.removeItem('token');
        setToken(null);
        setUserInfo(null);
        navigate('/signin');
    }
};