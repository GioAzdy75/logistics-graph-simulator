import { useState } from "react";
import { useEffect } from "react"; // arriba del todo si no lo tenés

import { MapContainer, TileLayer, Marker, Polyline, useMapEvents, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import "leaflet/dist/images/marker-icon.png";
import "leaflet/dist/images/marker-icon-2x.png";
import "leaflet/dist/images/marker-shadow.png";

import FormularioNuevoLocal from "../components/FormularioNuevoLocal";

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
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-yellow.png",
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const iconInicioRuta = new L.Icon({
  iconUrl: "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-green.png",
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const unirTramosRuta = (data) => {
  const coordenadas = [];
  const inicios = [];
  for (const tramo in data) {
    const nodos = data[tramo];
    if (!Array.isArray(nodos)) continue;
    if (nodos.length > 0) {
      inicios.push({ lat: nodos[0].lat, lon: nodos[0].lon });
    }
    for (let i = 0; i < nodos.length; i++) {
      const { lat, lon } = nodos[i];
      if (typeof lat !== "number" || typeof lon !== "number") continue;
      const punto = { lat, lon };
      if (
        coordenadas.length === 0 ||
        coordenadas[coordenadas.length - 1].lat !== lat ||
        coordenadas[coordenadas.length - 1].lon !== lon
      ) {
        coordenadas.push(punto);
      }
    }
  }
  return { coordenadas, inicios };
};

export default function MapaRutas({ puntos, setPuntos, ruta, setRuta }) {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [coordenadasTemp, setCoordenadasTemp] = useState(null);
  const [iniciosRuta, setIniciosRuta] = useState([]);
  const [pendienteDeCrear, setPendienteDeCrear] = useState(null);


  const eliminarPunto = async (id) => {
    try {
      const res = await fetch(`http://localhost:8000/punto/${id}`, {
        method: "DELETE"
      });
      if (res.ok) {
        setPuntos(puntos.filter(p => p.id !== id));
        console.log("Punto eliminado correctamente.");
      } else {
        console.error("Error al eliminar punto.");
      }
    } catch (error) {
      console.error("Error al eliminar punto:", error);
    }
  };

  useEffect(() => {
    const cargarPuntosIniciales = async () => {
      try {
        const token = localStorage.getItem("token");
        const res = await fetch("http://localhost:8000/puntos/mapa", {
          headers: {
            "Authorization": `Bearer ${token}`
          }
        });
        const data = await res.json();
        if (Array.isArray(data)) {
          setPuntos(data);
        } else {
          setPuntos([]);
          if (data.detail) {
            alert("No autorizado. Por favor, inicia sesión.");
            // Aquí podrías redirigir al login si tienes routing
          }
        }
      } catch (error) {
        console.error("Error al cargar los puntos iniciales:", error);
        setPuntos([]);
      }
    };

    cargarPuntosIniciales();
  }, []);


  const MapClickFormulario = () => {
    useMapEvents({
      click(e) {
        setCoordenadasTemp({ lat: e.latlng.lat, lon: e.latlng.lng });
        setMostrarFormulario(true);
      },
    });
    return null;
  };

  const agregarLocalConfirmado = (nuevoPunto) => {
    setPendienteDeCrear(nuevoPunto);
    setMostrarFormulario(false);
    setCoordenadasTemp(null);
  };

  const enviarLocal = async () => {
    const body = {
      from_: pendienteDeCrear.from,
      to: pendienteDeCrear.to,
      calle: pendienteDeCrear.calle,
      local: {
        id: pendienteDeCrear.id,
        name: pendienteDeCrear.nombre,
        lat: pendienteDeCrear.lat,
        lon: pendienteDeCrear.lon
      }
    };
    try {
      const res = await fetch("http://localhost:8000/ubicacion/insertar-local", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body)
      });
      const data = await res.json();
      setPuntos([...puntos, pendienteDeCrear]);
      setPendienteDeCrear(null);
      console.log("Local creado:", data);
    } catch (error) {
      console.error("Error al crear el punto:", error);
    }
  };

  const calcularRuta = async () => {
    try {
      const response = await fetch("http://localhost:8000/calcularRuta");
      const data = await response.json();
      const resultado = unirTramosRuta(data);
      setRuta(resultado.coordenadas);
      setIniciosRuta(resultado.inicios);
    } catch (error) {
      console.error("Error al calcular la ruta:", error);
    }
  };

  return (
    <section className="ml-64 p-6 relative z-10">
      <h2 className="text-2xl font-bold mb-4">Mapa Interactivo</h2>

      {mostrarFormulario && coordenadasTemp && (
        <FormularioNuevoLocal
          coordenadas={coordenadasTemp}
          onClose={() => {
            setMostrarFormulario(false);  // <- cierra el formulario
            setCoordenadasTemp(null);     // <- resetea la posición
          }}
          onCrear={(nuevoPunto) => {
            setPuntos([...puntos, nuevoPunto]);  // agrega nuevo marcador
            setMostrarFormulario(false);
            setCoordenadasTemp(null);
          }}
        />
      )}


      <div className="border border-gray-300 rounded-lg overflow-hidden relative z-0">
        <MapContainer center={[-32.89, -68.83]} zoom={13} className="h-96">
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <MapClickFormulario />

          {Array.isArray(puntos) && puntos.map((p, i) => (
            <Marker
              key={"punto-" + i}
              position={[p.lat, p.lon]}
              icon={p.tipo === "centro" ? iconCentro : iconLocal}
            >
              <Popup>
                <strong>{p.nombre || (p.tipo === "local" ? "Local" : "Centro")}</strong>
              </Popup>
            </Marker>
          ))}

          {pendienteDeCrear && (
            <Marker
              position={[pendienteDeCrear.lat, pendienteDeCrear.lon]}
              icon={pendienteDeCrear.tipo === "centro" ? iconCentro : iconLocal}
            >
              <Popup>
                <strong>{pendienteDeCrear.nombre}</strong>
              </Popup>
            </Marker>
          )}

          {iniciosRuta.map((p, i) => (
            <Marker
              key={"inicio-" + i}
              position={[p.lat, p.lon]}
              icon={iconInicioRuta}
            >
              <Popup>
                <strong>Inicio Ruta #{i + 1}</strong>
              </Popup>
            </Marker>
          ))}

          {Array.isArray(ruta) && ruta.length > 0 && ruta[0] && (
            <Polyline positions={ruta.map(p => [p.lat, p.lon])} color="blue" />
          )}
        </MapContainer>
      </div>

      {pendienteDeCrear && (
        <button
          onClick={enviarLocal}
          className="mt-4 bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 block mx-auto"
        >
          Crear Nuevo Punto
        </button>
      )}

      <button
        onClick={calcularRuta}
        className="mt-4 bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700 block mx-auto"
      >
        Calcular Ruta Óptima
      </button>

      {Array.isArray(puntos) && puntos.length > 0 && (
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
                  <th className="border px-4 py-2">Acciones</th>
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
                    <td className="border px-4 py-1">
                      <button
                        className="bg-red-600 text-white px-2 py-1 rounded hover:bg-red-700"
                        onClick={() => {
                          if (window.confirm("¿Estás seguro de eliminar este punto?")) {
                            eliminarPunto(p.id);
                          }
                        }}
                      >
                        Eliminar
                      </button>
                    </td>
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