import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function Sidebar() {
  const navigate = useNavigate();
  const { logout } = useAuth();

  const handleLogout = () => {
    logout();
  };

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen fixed top-0 left-0 z-20 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-semibold">Optimización de Rutas</h1>
        <p className="text-xs text-gray-400 mt-1">Sistema Logístico</p>
      </div>
      
      <nav className="flex-1 p-4 space-y-4 text-sm">
        <ul className="space-y-2">
          <li><Link to="/" className="text-blue-400 hover:underline">Introducción</Link></li>
          <li><Link to="/config" className="text-blue-400 hover:underline">Configuracion Mapa</Link></li>
          <li><Link to="/clients" className="text-blue-400 hover:underline">Clientes</Link></li>
          <li><Link to="/map" className="text-blue-400 hover:underline">Mapa</Link></li>
        </ul>
      </nav>

      {/* Sección de usuario al fondo */}
      <div className="p-4 border-t border-gray-700">
        <div className="mb-3">
          <div className="flex items-center space-x-2">
            <div className="w-8 h-8 bg-indigo-600 rounded-full flex items-center justify-center">
              <svg className="w-4 h-4 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium">Administrador</p>
              <p className="text-xs text-gray-400">admin@sistema</p>
            </div>
          </div>
        </div>
        
        <button
          onClick={handleLogout}
          className="w-full flex items-center space-x-2 px-3 py-2 text-sm text-gray-300 hover:text-white hover:bg-gray-800 rounded-md transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
          </svg>
          <span>Cerrar Sesión</span>
        </button>
      </div>
    </aside>
  );
}
