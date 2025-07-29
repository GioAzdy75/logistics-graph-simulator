import { BrowserRouter as Router, Route, Routes, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "./context/AuthContext";
import Sidebar from "./components/Sidebar.jsx";
import Introduction from "./pages/Introduction";
import MapaRutas from "./pages/MapaRutas";
import ConfigMap from "./pages/ConfigMap";
import Clients from "./pages/Clients";
import SecureLogin from "./pages/SecureLogin";

// Componente para proteger rutas
function ProtectedRoute({ children }) {
  const { isAuthenticated } = useAuth();
  return isAuthenticated ? children : <Navigate to="/login" replace />;
}

// Layout principal de la aplicación
function AppLayout() {
  return (
    <div className="bg-gray-50 min-h-screen flex pl-64">
      <Sidebar />
      <main className="flex-1 overflow-y-auto">
        <Routes>
          <Route path="/" element={<ProtectedRoute><Introduction /></ProtectedRoute>} />
          <Route path="/config" element={<ProtectedRoute><ConfigMap/></ProtectedRoute>}/>
          <Route path="/clients" element={<ProtectedRoute><Clients/></ProtectedRoute>}/>
          <Route path="/map" element={<ProtectedRoute><MapaRutas /></ProtectedRoute>} />
        </Routes>
      </main>
    </div>
  );
}

export default function App() {
  return (
    <Router>
      <AuthProvider>
        <Routes>
          {/* Ruta de login sin protección */}
          <Route path="/login" element={<SecureLogin />} />
          
          {/* Todas las demás rutas protegidas */}
          <Route path="/*" element={<AppLayout />} />
        </Routes>
      </AuthProvider>
    </Router>
  );
}