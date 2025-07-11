import React, { useState, useRef } from "react";
import { OpenStreetMapProvider } from "leaflet-geosearch";
import { v4 as uuidv4 } from "uuid";
import { MapContainer, TileLayer, Marker, useMap } from "react-leaflet";

import L from "leaflet";
import "leaflet/dist/leaflet.css";


const tipos = ["minorista", "mayorista", "franquicia", "otro"];

// Fix iconos en React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png",
  iconRetinaUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png",
  shadowUrl: "https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png",
});

/* --- Componente para mover el mapa al punto --- */
function ChangeView({ center }) {
  const map = useMap();
  map.setView(center, 17);
  return null;
}

export default function Clients() {
  const provider = useRef(new OpenStreetMapProvider());

  /* ---------- Estados de formulario ---------- */
  const [name, setName]           = useState("");
  const [direccion, setDireccion] = useState("");
  const [tipo, setTipo]           = useState(tipos[0]);
  const [tramo, setTramo] = useState(null);


  /* ---------- Estados de proceso ---------- */
  const [coordenadas, setCoord]    = useState(null); // { lat, lon }
  const [loading, setLoading]      = useState(false);
  const [mensaje, setMensaje]      = useState("");

  /* ---------- Geocodificar dirección ---------- */
  const geocodificar = async () => {
    setMensaje("");
    if (!direccion.trim()) return;
    const results = await provider.current.search({ query: direccion });
    if (results.length) {
      const { x, y, label } = results[0];
      setDireccion(label);
      setCoord({ lat: y, lon: x }); // ← esto activa el mapa
      await fetchTramoCercano({ lat: y, lon: x });
    } else {
      setMensaje("No se encontró la dirección.");
    }
  };

  /* --- */
  const fetchTramoCercano = async (coords) => {
  const res = await fetch("http://localhost:8000/ubicacion/tramo-cercano", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(coords),
  });
  if (!res.ok) throw new Error("Error tramo cercano");
  const data = await res.json();           // { calle, from, to }
  setTramo(data);                          // guardamos para luego
  return data;
};


  /* ---------- Enviar al backend ---------- */
  const handleSubmit = async (e) => {
  e.preventDefault();
  setMensaje("");

  /* ── Validaciones previas ─────────────────────────── */
  if (!coordenadas) {
    setMensaje("Primero geocodifica la dirección.");
    return;
  }
  if (!tramo) {
    setMensaje("Falta calcular el tramo cercano. Geocodifica o mueve el marcador.");
    return;
  }

  setLoading(true);
  try {
    /* ── Construir payload final ────────────────────── */
    const payload = {
      from_: tramo.from,     // 🔑  renombrado
      to:    tramo.to,
      calle: tramo.calle,
      local: {
        id:   uuidv4(),
        name,
        lat:  coordenadas.lat,
        lon:  coordenadas.lon,
        tipo,
      },
    };

    /* ── Enviar al backend ──────────────────────────── */
    const res = await fetch(
      "http://localhost:8000/ubicacion/insertar-local",
      {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }
    );

    if (res.ok) {
      setMensaje("✅ Cliente creado correctamente");
      /* limpiar formulario */
      setName("");
      setDireccion("");
      setCoord(null);
      setTramo(null);
    } else {
      throw new Error("Error al insertar");
    }
  } catch (err) {
    setMensaje("❌ " + err.message);
  } finally {
    setLoading(false);
  }
};

  return (
    <div className="max-w-xl mx-auto p-6">
      <h1 className="text-2xl font-bold mb-4">Alta de Cliente</h1>

      <form onSubmit={handleSubmit} className="space-y-4">
        {/* Nombre */}
        <div>
          <label className="block font-semibold mb-1">Nombre</label>
          <input
            value={name}
            onChange={(e) => setName(e.target.value)}
            className="w-full border rounded px-3 py-2"
            required
          />
        </div>

        {/* Dirección */}
        <div>
          <label className="block font-semibold mb-1">Dirección</label>
          <div className="flex gap-2">
            <input
              value={direccion}
              onChange={(e) => setDireccion(e.target.value)}
              className="flex-1 border rounded px-3 py-2"
              required
            />
            <button
              type="button"
              onClick={geocodificar}
              className="bg-blue-600 text-white px-4 rounded hover:bg-blue-700"
            >
              Geocodificar
            </button>
          </div>
          {coordenadas && (
            <p className="text-sm text-gray-600 mt-1">
              Lat: {coordenadas.lat.toFixed(5)} | Lon: {coordenadas.lon.toFixed(5)}
            </p>
          )}
        </div>

        {/* Tipo */}
        <div>
          <label className="block font-semibold mb-1">Tipo de local</label>
          <select
            value={tipo}
            onChange={(e) => setTipo(e.target.value)}
            className="w-full border rounded px-3 py-2"
          >
            {tipos.map((t) => (
              <option key={t} value={t}>
                {t}
              </option>
            ))}
          </select>
        </div>

        {coordenadas && (
          <div className="mt-6">
            <h2 className="font-semibold mb-2">Ubicación geocodificada</h2>
            <div className="w-full h-96 rounded shadow border overflow-hidden">
              <MapContainer center={coordenadas} zoom={17} className="w-full h-full">
                <ChangeView center={coordenadas} />
                <TileLayer
                  attribution='&copy; OpenStreetMap'
                  url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                />
                <Marker
                  position={coordenadas}
                  draggable={true}
                  eventHandlers={{
                    dragend: async (e) => {
                      const newPos = e.target.getLatLng();
                      setCoord({ lat: newPos.lat, lon: newPos.lng });
                      await fetchTramoCercano({ lat: newPos.lat, lon: newPos.lng });
                    },
                  }}
                />
              </MapContainer>
            </div>
          </div>
        )}

        {tramo && (
          <p className="mt-2 text-sm text-gray-700">
            Calle detectada: <span className="font-semibold">{tramo.calle}</span>
          </p>
        )}


        {/* Botón */}
        <button
          type="submit"
          className="w-full bg-green-600 text-white py-2 rounded hover:bg-green-700 disabled:opacity-50"
          disabled={loading}
        >
          {loading ? "Guardando..." : "Guardar cliente"}
        </button>
      </form>

      {/* Mensajes */}
      {mensaje && <p className="mt-4">{mensaje}</p>}
    </div>
  );
}
