import { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Introduction from "./pages/Introduction";
import MapaRutas from "./pages/MapaRutas";
import Login from "./pages/Login";
import PrivateRoute from "./components/PrivateRoute";

export default function App() {
  const [puntos, setPuntos] = useState([]);
  const [ruta, setRuta] = useState([]);
  const [isLogged, setIsLogged] = useState(!!localStorage.getItem("token"));

  return (
    <Router>
      <div className="bg-gray-50 min-h-screen flex">
        <Sidebar />
        <main className="flex-1">
          <Routes>
            <Route path="/login" element={<Login onLogin={() => setIsLogged(true)} />} />
            <Route path="/" element={<Introduction />} />
            <Route path="/locales" element={
              <PrivateRoute>
                <MapaRutas puntos={puntos} setPuntos={setPuntos} ruta={ruta} setRuta={setRuta} />
              </PrivateRoute>
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
