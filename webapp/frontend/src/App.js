import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import Introduction from "./pages/Introduction";
import MapaRutas from "./pages/MapaRutas";
import ConfigMap from "./pages/ConfigMap";
import Clients from "./pages/Clients";

export default function App() {
  return (
    <Router>
      <div className="bg-gray-50 min-h-screen flex pl-64">
        <Sidebar />
        <main className="flex-1 overflow-y-auto">
          <Routes>
            <Route path="/" element={<Introduction />} />
            <Route path="/config" element={<ConfigMap/>}/>
            <Route path="/clients" element={<Clients/>}/>
            <Route path="/map" element={<MapaRutas />} />
          </Routes>
        </main>
      </div>
    </Router>
  );
}