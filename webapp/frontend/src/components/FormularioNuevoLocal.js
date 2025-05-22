import { useEffect, useState } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import L from "leaflet";

const iconLocal = new L.Icon({
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

export default function FormularioNuevoLocal({ coordenadas, onClose, onCrear }) {
  const [nombre, setNombre] = useState("");
  const [tipo, setTipo] = useState("local");
  const [calles, setCalles] = useState([]);
  const [calleSeleccionada, setCalleSeleccionada] = useState("");
  const [tramoSeleccionado, setTramoSeleccionado] = useState(null);
  const [confirmado, setConfirmado] = useState(false);

  useEffect(() => {
    const obtenerTramo = async () => {
      try {
        const res = await fetch("http://localhost:8000/ubicacion/tramo-cercano", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(coordenadas),
        });
        const data = await res.json();
        setTramoSeleccionado(data);
        setCalles([data.calle]); // Por ahora solo una, luego se puede expandir
        setCalleSeleccionada(data.calle);
      } catch (error) {
        console.error("Error obteniendo tramo cercano:", error);
      }
    };
    obtenerTramo();
  }, [coordenadas]);

  const handleConfirmar = () => {
    if (!nombre || !calleSeleccionada) return;
    setConfirmado(true);
  };

  const handleCrear = async () => {
    if (!tramoSeleccionado || !confirmado) return;

    const body = {
      from_: tramoSeleccionado.from,
      to: tramoSeleccionado.to,
      calle: calleSeleccionada,
      local: {
        id: `P-${Date.now()}`, // o podés usar uuid()
        name: nombre,
        lat: coordenadas.lat,
        lon: coordenadas.lon,
        tipo: tipo === "centro" ? "CentroDeDistribucion" : "Local" // ✅ traducimos a los valores esperados en Neo4j
      }
    };

    try {
      await fetch("http://localhost:8000/ubicacion/insertar-local", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      onCrear({
        nombre,
        lat: coordenadas.lat,
        lon: coordenadas.lon,
        tipo,
      });
      onClose();
    } catch (error) {
      console.error("Error al crear nuevo punto:", error);
    }
  };

  return (
    <div className="fixed top-20 left-1/2 transform -translate-x-1/2 w-96 bg-white p-4 rounded shadow-2xl z-50 border">
      <h3 className="text-lg font-semibold mb-2">Nuevo Punto</h3>

      <input
        type="text"
        placeholder="Nombre"
        className="w-full border px-3 py-2 mb-3 rounded"
        value={nombre}
        onChange={(e) => setNombre(e.target.value)}
      />

      <select
        className="w-full border px-3 py-2 mb-3 rounded"
        value={tipo}
        onChange={(e) => setTipo(e.target.value)}
      >
        <option value="local">Local</option>
        <option value="centro">Centro de Distribución</option>
      </select>

      <select
        className="w-full border px-3 py-2 mb-3 rounded"
        value={calleSeleccionada}
        onChange={(e) => setCalleSeleccionada(e.target.value)}
      >
        {calles.map((c, i) => (
          <option key={i} value={c}>
            {c}
          </option>
        ))}
      </select>

      <button
        className="w-full bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 mb-2"
        onClick={handleConfirmar}
        disabled={!nombre}
      >
        Confirmar ubicación
      </button>

      {confirmado && (
        <>
          <div className="h-48 border rounded mb-3 overflow-hidden relative z-40">
            <MapContainer center={[coordenadas.lat, coordenadas.lon]} zoom={17} className="h-full z-40">
              <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
              <Marker position={[coordenadas.lat, coordenadas.lon]} icon={iconLocal}>
                <Popup>{nombre}</Popup>
              </Marker>
            </MapContainer>
          </div>

          <button
            className="w-full bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
            onClick={handleCrear}
          >
            Crear Nuevo Punto
          </button>
        </>
      )}

      <button
        className="mt-2 w-full bg-gray-300 text-gray-700 px-4 py-2 rounded hover:bg-gray-400"
        onClick={onClose}
      >
        Cancelar
      </button>
    </div>
  );
}
