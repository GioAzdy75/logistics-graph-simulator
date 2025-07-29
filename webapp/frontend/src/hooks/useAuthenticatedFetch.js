import { useState } from 'react';
import { useAuth } from './AuthContext';

export function useAuthenticatedFetch() {
  const { logout } = useAuth();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const authenticatedFetch = async (url, options = {}) => {
    setLoading(true);
    setError(null);

    try {
      const token = localStorage.getItem('token');
      
      if (!token) {
        logout();
        throw new Error('No hay token de autenticación');
      }

      const headers = {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
        ...options.headers,
      };

      const response = await fetch(url, {
        ...options,
        headers,
      });

      // Si el token expiró o es inválido, logout automático
      if (response.status === 401) {
        logout();
        throw new Error('Sesión expirada');
      }

      if (!response.ok) {
        throw new Error(`Error ${response.status}: ${response.statusText}`);
      }

      const data = await response.json();
      return data;

    } catch (err) {
      setError(err.message);
      throw err;
    } finally {
      setLoading(false);
    }
  };

  return { authenticatedFetch, loading, error };
}
