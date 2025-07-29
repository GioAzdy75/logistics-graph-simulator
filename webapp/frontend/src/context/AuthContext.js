import { createContext, useContext, useState, useEffect, useCallback } from "react";
import { useNavigate } from "react-router-dom";

export const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const navigate = useNavigate();
  const [isAuthenticated, setIsAuthenticated] = useState(() => !!localStorage.getItem("token"));

  /* ---------- API pública del contexto ---------- */
  const login = useCallback((token) => {
    localStorage.setItem("token", token);
    setIsAuthenticated(true);
    navigate("/", { replace: true });
  }, [navigate]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    navigate("/login", { replace: true });
  }, [navigate]);

  /* ---------- Sincronizamos pestañas ---------- */
  useEffect(() => {
    const listener = (e) => {
      if (e.key === "token") setIsAuthenticated(!!e.newValue);
    };
    window.addEventListener("storage", listener);
    return () => window.removeEventListener("storage", listener);
  }, []);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  return useContext(AuthContext);
}
