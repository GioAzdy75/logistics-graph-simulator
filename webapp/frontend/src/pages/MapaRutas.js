import { useState } from "react";
import { MapContainer, TileLayer, Marker, Polyline, useMapEvents, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import "leaflet/dist/images/marker-icon.png";
import "leaflet/dist/images/marker-icon-2x.png";
import "leaflet/dist/images/marker-shadow.png";

delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});


const iconLocal = new L.Icon({
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const iconCentro = new L.Icon({
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  iconSize: [30, 50],
  iconAnchor: [15, 50],
  popupAnchor: [1, -34],
});


export default function MapaRutas({ puntos, setPuntos, ruta, setRuta }) {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [nuevoNombre, setNuevoNombre] = useState("");
  const [nuevoTipo, setNuevoTipo] = useState("local");
  const [coordenadasTemp, setCoordenadasTemp] = useState(null);

  const MapClickFormulario = () => {
    useMapEvents({
      click(e) {
        setCoordenadasTemp({ lat: e.latlng.lat, lon: e.latlng.lng });
      },
    });
    return null;
  };

  const agregarNuevoPunto = async () => {
    if (nuevoNombre && coordenadasTemp) {
      const nuevoPunto = {
        nombre: nuevoNombre,
        lat: coordenadasTemp.lat,
        lon: coordenadasTemp.lon,
        tipo: nuevoTipo,
      };
      setPuntos([...puntos, nuevoPunto]);

      try {
        await fetch("http://localhost:8000/agregar-punto", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(nuevoPunto),
        });
        console.log("Punto registrado en la base de datos.");
      } catch (error) {
        console.error("Error al guardar el punto en la API:", error);
      }

      setNuevoNombre("");
      setNuevoTipo("local");
      setCoordenadasTemp(null);
      setMostrarFormulario(false);
    }
  };

  const calcularRuta = async () => {
    const response = await fetch("http://localhost:8000/calcular-ruta", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ puntos }),
    });
    const data = await response.json();
    setRuta(data.ruta);
  };

  return (
    <section className="ml-64 p-6 relative z-10">
      <h2 className="text-2xl font-bold mb-4">Mapa Interactivo</h2>

      <button
        className="mb-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        onClick={() => setMostrarFormulario(true)}
      >
        Agregar Punto
      </button>

      {mostrarFormulario && (
        <div className="fixed top-20 left-1/2 transform -translate-x-1/2 w-96 bg-white p-4 rounded shadow-2xl z-50 border">
          <h3 className="text-lg font-semibold mb-2">Nuevo Punto</h3>
          <input
            type="text"
            placeholder="Nombre"
            className="w-full border px-3 py-2 mb-3 rounded"
            value={nuevoNombre}
            onChange={(e) => setNuevoNombre(e.target.value)}
          />
          <select
            className="w-full border px-3 py-2 mb-3 rounded"
            value={nuevoTipo}
            onChange={(e) => setNuevoTipo(e.target.value)}
          >
            <option value="local">Local</option>
            <option value="centro">Centro de Distribución</option>
          </select>
          <div className="h-48 border rounded mb-3 overflow-hidden relative z-40">
            <MapContainer center={[-32.89, -68.83]} zoom={13} className="h-full z-40">
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <MapClickFormulario />
              {coordenadasTemp && (
                <Marker position={[coordenadasTemp.lat, coordenadasTemp.lon]} />
              )}
            </MapContainer>
          </div>
          <div className="flex justify-end gap-2">
            <button
              className="bg-green-600 text-white px-3 py-1 rounded hover:bg-green-700"
              onClick={agregarNuevoPunto}
            >
              Confirmar
            </button>
            <button
              className="bg-gray-300 text-gray-700 px-3 py-1 rounded hover:bg-gray-400"
              onClick={() => setMostrarFormulario(false)}
            >
              Cancelar
            </button>
          </div>
        </div>
      )}

      <div className="border border-gray-300 rounded-lg overflow-hidden relative z-0">
        <MapContainer center={[-32.89, -68.83]} zoom={13} className="h-96">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          {puntos.map((p, i) => (
            <Marker
              key={i}
              position={[p.lat, p.lon]}
              icon={p.tipo === "centro" ? iconCentro : iconLocal}
            >
              <Popup>
                <strong>{p.nombre || (p.tipo === "local" ? "Local" : "Centro")}</strong>
              </Popup>
            </Marker>
          ))}

          {ruta.length > 0 && (
            <Polyline positions={ruta.map((p) => [p.lat, p.lon])} color="blue" />
          )}
        </MapContainer>
      </div>

      <button
        onClick={calcularRuta}
        className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 block mx-auto"
      >
        Calcular Ruta Óptima
      </button>

      {puntos.length > 0 && (
        <div className="mt-8">
          <h3 className="text-xl font-semibold mb-2 text-center">Puntos Agregados</h3>
          <div className="overflow-x-auto">
            <table className="min-w-full table-auto border border-gray-300 text-sm">
              <thead className="bg-gray-100">
                <tr>
                  <th className="border px-4 py-2">#</th>
                  <th className="border px-4 py-2">Nombre</th>
                  <th className="border px-4 py-2">Latitud</th>
                  <th className="border px-4 py-2">Longitud</th>
                  <th className="border px-4 py-2">Tipo</th>
                </tr>
              </thead>
              <tbody>
                {puntos.map((p, i) => (
                  <tr key={i} className="text-center">
                    <td className="border px-4 py-1">{i + 1}</td>
                    <td className="border px-4 py-1">{p.nombre || "-"}</td>
                    <td className="border px-4 py-1">{p.lat.toFixed(5)}</td>
                    <td className="border px-4 py-1">{p.lon.toFixed(5)}</td>
                    <td className="border px-4 py-1">{p.tipo}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}
