import { useState } from "react";
import { useEffect } from "react"; // arriba del todo si no lo tenés

import { MapContainer, TileLayer, Marker, Polyline, useMapEvents, Popup, Tooltip } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

import "leaflet/dist/images/marker-icon.png";
import "leaflet/dist/images/marker-icon-2x.png";
import "leaflet/dist/images/marker-shadow.png";

import FormularioNuevoLocal from "../components/FormularioNuevoLocal";
import PolylineDecorator from "../components/PolylineDecorator"

import "leaflet-polylinedecorator";

import { iconLocal, iconCentro } from '../static/Icons';
import {unirTramosRuta} from '../utils/unirRutas'

const getAngle = (p1, p2) => {
  const dx = p2.lon - p1.lon;
  const dy = p2.lat - p1.lat;
  return (Math.atan2(dy, dx) * 180) / Math.PI;
};

const crearFlechaIcono = (angle) =>
  L.divIcon({
    className: "flecha-icono",
    html: `
      <div style="
        transform: rotate(${angle}deg);
        font-size: 20px;
        color: red;
      ">
        ➤
      </div>
    `,
    iconSize: [20, 20],
    iconAnchor: [10, 10],
  });

  
const getSegmentos = (ruta) => {
  const segmentos = [];
  for (let i = 0; i < ruta.length - 1; i++) {
    segmentos.push({
      start: ruta[i],
      end: ruta[i + 1],
      index: i,
    });
  }
  return segmentos;
};

const getColorGradient = (index, total) => {
  const hueStart = 240; // azul oscuro
  const hueEnd = 0;     // rojo

  // Invertido: de azul a rojo
  const hue = hueStart + ((hueEnd - hueStart) * index) / (total || 1);

  return `hsl(${hue}, 100%, 30%)`;
};


const getIconoPorTipo = (tipo) => tipo === "CentroDeDistribucion" ? iconCentro : iconLocal;

// Crea un ícono con número dinámico
const crearIconoConNumero = (numero, iconBase) =>
  L.divIcon({
    className: "custom-icon",
    html: `
      <div style="position: relative; display: inline-block;">
        <img src="${iconBase.options.iconUrl}" style="width: 25px; height: 41px;" />
        <div style="
          position: absolute;
          top: -5px;
          left: 0;
          width: 100%;
          text-align: center;
          font-weight: bold;
          font-size: 14px;
          color: white;
          text-shadow: 1px 1px 2px black;
        ">
          ${numero}
        </div>
      </div>
    `,
    iconSize: [25, 41],
    iconAnchor: [12, 41],
    popupAnchor: [0, -41],
  });


export default function MapaRutas({}) {
  const [mostrarFormulario, setMostrarFormulario] = useState(false);
  const [coordenadasTemp, setCoordenadasTemp] = useState(null);
  const [iniciosRuta, setIniciosRuta] = useState([]);
  const [pendienteDeCrear, setPendienteDeCrear] = useState(null);
  const [puntos, setPuntos] = useState(null)
  const [ruta, setRuta] = useState(null)
  //eliminar Puntos - Verificar Reponsabilidad
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
  
  //cargar puntos
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

  //Obtiene coordenadas del mapa
  const MapClickFormulario = () => {
    useMapEvents({
      click(e) {
        setCoordenadasTemp({ lat: e.latlng.lat, lon: e.latlng.lng });
        setMostrarFormulario(true);
      },
    });
    return null;
  };
  //
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
            setMostrarFormulario(false);
            setCoordenadasTemp(null);
          }}
          onCrear={(nuevoPunto) => {
            setPuntos([...puntos, nuevoPunto]);
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
              icon={p.tipo === "CentroDeDistribucion" ? iconCentro : iconLocal}
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
              icon={getIconoPorTipo(p.tipo)} // no tiene TIPO ver que alternativa usar (se me ocurre desde la api mandarle)
            >
              <Popup>
                <strong>Inicio Ruta #{i + 1}</strong>
              </Popup>
              <Tooltip
                direction="top"
                offset={[0, -20]}
                permanent
                opacity={1}
              >
                <span style={{
                  fontWeight: "bold",
                  color: "white",
                  textShadow: "1px 1px 2px black",
                  fontSize: "14px"
                }}>
                  {i + 1}
                </span>
              </Tooltip>
            </Marker>
          ))}
          {Array.isArray(ruta) && ruta.length > 0 && ruta[0] && (
            <>
              {getSegmentos(ruta).map(({ start, end, index }, i, arr) => (
                <Polyline
                  key={`segmento-${i}`}
                  positions={[
                    [start.lat, start.lon],
                    [end.lat, end.lon],
                  ]}
                  color={getColorGradient(index, arr.length - 1)}
                  weight={4}
                  opacity={0.8}
                />
              ))}

              <PolylineDecorator positions={ruta.map(p => [p.lat, p.lon])} />
            </>
          )}
        </MapContainer>
      </div>

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