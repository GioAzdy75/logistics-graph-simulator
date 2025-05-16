import { useState } from "react";
import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Introduction from "./pages/Introduction";
import MapaRutas from "./pages/MapaRutas";

export default function App() {
  const [puntos, setPuntos] = useState([]);
  const [ruta, setRuta] = useState([]);

  return (
    <Router>
      <div className="bg-gray-50 min-h-screen flex">
        <Sidebar />
        <main className="flex-1">
          <Routes>
            <Route path="/" element={<Introduction />} />
            <Route path="/locales" element={
              <MapaRutas puntos={puntos} setPuntos={setPuntos} ruta={ruta} setRuta={setRuta} />
            } />
          </Routes>
        </main>
      </div>
    </Router>
  );
}
