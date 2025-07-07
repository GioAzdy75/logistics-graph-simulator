import React, { useState, useRef } from "react";
import { MapContainer, TileLayer, Marker, Circle, useMap } from "react-leaflet";
import { OpenStreetMapProvider } from "leaflet-geosearch";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

/* --- Fix para iconos de Leaflet en React --- */
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl:   "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl:
    "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

/* --- Mueve el mapa cuando cambian las coordenadas --- */
function ChangeView({ center, zoom }) {
  const map = useMap();
  map.setView(center, zoom);
  return null;
}

export default function ConfigMap() {
  /* ---------- Estados ---------- */
  const [query, setQuery] = useState("");
  const [center, setCenter] = useState([-32.8908, -68.8272]); // Mendoza por defecto
  const [radio, setRadio] = useState(5000);                   // metros
  const provider = useRef(new OpenStreetMapProvider());

  /* ---------- Geocodificar texto ---------- */
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!query.trim()) return;
    const results = await provider.current.search({ query });
    if (results.length) {
      const { x, y, label } = results[0];
      setCenter([y, x]);          // [lat, lng]
      setQuery(label);            // normalizar texto
    }
  };

  /* ---------- Enviar datos ---------- */
  const handleSubmit = async () => {
    const payload = { location: query, radio };
    try {
      const res = await fetch("http://localhost:8000/Mapa", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      });
      if (res.ok) alert("Mapa generado con éxito 🎉");
      else alert("Error al generar mapa");
    } catch (err) {
      alert("Error de red");
    }
  };

  return (
    <div className="flex flex-col gap-4 h-full p-4">
      {/* ---------- Búsqueda de ciudad ---------- */}
      <form onSubmit={handleSearch} className="flex gap-2">
        <input
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ciudad / provincia (ej. Plaza Independencia, Mendoza)"
          className="flex-1 border rounded px-3 py-2"
        />
        <button
          type="submit"
          className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700"
        >
          Buscar
        </button>
      </form>

      {/* ---------- Control de radio ---------- */}
      <div className="flex items-center gap-4">
        <label className="font-semibold">Radio (m):</label>
        <input
          type="number"
          value={radio}
          min={100}
          step={100}
          onChange={(e) => setRadio(Number(e.target.value))}
          className="border rounded px-3 py-1 w-32"
        />
        <input
          type="range"
          min="100"
          max="20000"
          step="100"
          value={radio}
          onChange={(e) => setRadio(Number(e.target.value))}
          className="flex-1"
        />
      </div>

      {/* ---------- Mapa ---------- */}
      <div className="flex-1">
        <MapContainer center={center} zoom={13} style={{ height: "100%", width: "100%" }}>
          <ChangeView center={center} zoom={13} />
          <TileLayer
            attribution='&copy; OpenStreetMap'
            url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
          />
          <Marker position={center} />
          <Circle center={center} radius={radio} pathOptions={{ fillOpacity: 0.2 }} />
        </MapContainer>
      </div>

      {/* ---------- Botón final ---------- */}
      <button
        onClick={handleSubmit}
        className="self-end bg-green-600 text-white px-6 py-2 rounded hover:bg-green-700"
      >
        Generar mapa
      </button>
    </div>
  );
}
