import { Link, useNavigate } from "react-router-dom";

export default function Sidebar() {
  const navigate = useNavigate();

  return (
    <aside className="w-64 bg-gray-900 text-white h-screen fixed top-0 left-0 z-20 flex flex-col">
      <div className="p-4 border-b border-gray-700">
        <h1 className="text-lg font-semibold">Optimización de Rutas</h1>
      </div>
      <nav className="flex-1 p-4 space-y-4 text-sm">
        <ul className="space-y-2">
          <li><Link to="/" className="text-blue-400 hover:underline">Introducción</Link></li>
          <li><Link to="/config" className="text-blue-400 hover:underline">Configuracion Mapa</Link></li>
          <li><Link to="/clients" className="text-blue-400 hover:underline">Clientes</Link></li>
          <li><Link to="/map" className="text-blue-400 hover:underline">Mapa</Link></li>
        </ul>
      </nav>
    </aside>
  );
}
