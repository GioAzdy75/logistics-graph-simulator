import React, { useState, useEffect, useRef } from 'react';
import { MapContainer, TileLayer, Marker, Circle, useMapEvents, useMap } from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";

// Importar iconos
import { iconLocal, iconCentro } from '../static/Icons';

// Función para obtener el ícono por tipo
const getIconoPorTipo = (tipo) => tipo === "CentroDeDistribucion" ? iconCentro : iconLocal;

const ConfigMap = () => {
  const [puntos, setPuntos] = useState([]);
  const [centroSeleccionado, setCentroSeleccionado] = useState(null);
  const [radio, setRadio] = useState(1000); // Radio en metros, valor inicial 1km
  const [coordenadasCirculo, setCoordenadasCirculo] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [mensaje, setMensaje] = useState('');
  const [centroMapa, setCentroMapa] = useState([-38.4161, -63.6167]); // Centro de Argentina
  const [zoomMapa, setZoomMapa] = useState(5); // Zoom para ver toda Argentina
  const mapRef = useRef(null);
  
  // Componente para actualizar la vista del mapa
  const MapUpdater = () => {
    const map = useMap();
    
    useEffect(() => {
      if (centroMapa && centroMapa[0] !== 0 && centroMapa[1] !== 0) {
        console.log("Actualizando vista del mapa a:", centroMapa, "zoom:", zoomMapa);
        map.setView(centroMapa, zoomMapa);
      }
    }, [centroMapa, zoomMapa, map]);
    
    return null;
  };
  
  // Obtener ubicación del usuario
  useEffect(() => {
    console.log("Intentando obtener geolocalización...");
    if ("geolocation" in navigator) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          const { latitude, longitude } = position.coords;
          console.log("¡Geolocalización exitosa!", latitude, longitude);
          setCentroMapa([latitude, longitude]);
          setZoomMapa(12);
        },
        (error) => {
          console.log("Error de geolocalización:", error.message);
          console.log("Manteniendo centro de Argentina");
        },
        {
          enableHighAccuracy: true,
          timeout: 10000,
          maximumAge: 60000
        }
      );
    } else {
      console.log("Geolocalización no disponible");
    }
  }, []);
  
  // Cargar puntos del mapa
  useEffect(() => {
    const cargarPuntos = async () => {
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
        }
      } catch (error) {
        console.error("Error al cargar los puntos:", error);
        setPuntos([]);
      }
    };

    cargarPuntos();
  }, []);

  // Componente para manejar clics en el mapa
  const MapClickHandler = () => {
    useMapEvents({
      click: (e) => {
        const { lat, lng } = e.latlng;
        setCoordenadasCirculo({ lat, lng });
        setCentroSeleccionado({ lat, lng });
        setMensaje(''); // Limpiar mensajes anteriores
      }
    });
    return null;
  };

  // Función para crear el mapa del cliente
  const crearMapaCliente = async () => {
    if (!centroSeleccionado) {
      alert("Por favor, selecciona un punto central en el mapa");
      return;
    }

    setCargando(true);
    setMensaje('Creando mapa logístico...');

    try {
      const token = localStorage.getItem("token");
      
      // Convertir coordenadas a string de ubicación (puedes mejorar esto con geocoding reverso)
      const location = `${centroSeleccionado.lat},${centroSeleccionado.lng}`;
      
      const response = await fetch("http://localhost:8000/Mapa", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Authorization": `Bearer ${token}`
        },
        body: JSON.stringify({
          location: location,
          radio: radio
        })
      });

      if (response.ok) {
        const result = await response.json();
        setMensaje('¡Mapa creado exitosamente!');
        console.log("Resultado:", result);
        
        // Recargar puntos para mostrar los nuevos
        setTimeout(async () => {
          const res = await fetch("http://localhost:8000/puntos/mapa", {
            headers: {
              "Authorization": `Bearer ${token}`
            }
          });
          const data = await res.json();
          if (Array.isArray(data)) {
            setPuntos(data);
          }
          setMensaje('¡Mapa cargado completamente!');
        }, 1000);
        
      } else {
        const error = await response.json();
        setMensaje(`Error al crear el mapa: ${error.detail || 'Error desconocido'}`);
      }
    } catch (error) {
      console.error("Error al crear mapa:", error);
      setMensaje('Error de conexión al crear el mapa');
    } finally {
      setCargando(false);
    }
  };

  return (
    <div className="p-6 h-full">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Configuración del Mapa del Cliente</h1>
      
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 h-full">
        {/* Panel de controles */}
        <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold text-gray-800 mb-4">Configuración de Área</h2>
          
          {/* Control de radio */}
          <div className="mb-6">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Radio de cobertura: {radio}m
            </label>
            <input
              type="range"
              min="100"
              max="5000"
              step="100"
              value={radio}
              onChange={(e) => setRadio(parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>100m</span>
              <span>5km</span>
            </div>
          </div>

          {/* Información del centro seleccionado */}
          {centroSeleccionado && (
            <div className="mb-6 p-4 bg-blue-50 rounded-lg">
              <h3 className="font-medium text-blue-900 mb-2">Centro Seleccionado</h3>
              <p className="text-sm text-blue-700">
                Lat: {centroSeleccionado.lat.toFixed(6)}
              </p>
              <p className="text-sm text-blue-700">
                Lng: {centroSeleccionado.lng.toFixed(6)}
              </p>
            </div>
          )}

          {/* Instrucciones */}
          <div className="mb-6 p-4 bg-yellow-50 rounded-lg">
            <h3 className="font-medium text-yellow-900 mb-2">Instrucciones</h3>
            <p className="text-sm text-yellow-700">
              1. Haz clic en el mapa para seleccionar el centro de tu área de cobertura
            </p>
            <p className="text-sm text-yellow-700">
              2. Ajusta el radio con el slider
            </p>
            <p className="text-sm text-yellow-700">
              3. Haz clic en "Crear Mapa" para confirmar
            </p>
          </div>

          {/* Indicador de estado */}
          {mensaje && (
            <div className={`mb-6 p-4 rounded-lg ${
              mensaje.includes('Error') ? 'bg-red-50 text-red-700' : 
              mensaje.includes('exitosamente') || mensaje.includes('completamente') ? 'bg-green-50 text-green-700' :
              'bg-blue-50 text-blue-700'
            }`}>
              <p className="text-sm font-medium">{mensaje}</p>
            </div>
          )}

          {/* Botón para crear mapa */}
          <button
            onClick={crearMapaCliente}
            disabled={!centroSeleccionado || cargando}
            className={`w-full py-3 px-4 rounded-lg font-medium transition-colors flex items-center justify-center ${
              (!centroSeleccionado || cargando)
                ? 'bg-gray-300 text-gray-500 cursor-not-allowed'
                : 'bg-blue-600 hover:bg-blue-700 text-white'
            }`}
          >
            {cargando ? (
              <>
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Creando Mapa...
              </>
            ) : (
              'Crear Mapa del Cliente'
            )}
          </button>
        </div>

        {/* Mapa */}
        <div className="lg:col-span-3 bg-white rounded-lg shadow-md overflow-hidden">
          <MapContainer
            center={centroMapa}
            zoom={zoomMapa}
            style={{ height: "600px", width: "100%" }}
            className="z-0"
          >
            <TileLayer
              url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
            />
            
            {/* Componente para actualizar la vista */}
            <MapUpdater />
            
            {/* Manejador de clics */}
            <MapClickHandler />
            
            {/* Mostrar puntos existentes */}
            {puntos.map((punto) => (
              <Marker
                key={punto.id}
                position={[punto.lat, punto.lon]}
                icon={getIconoPorTipo(punto.tipo)}
              >
              </Marker>
            ))}
            
            {/* Círculo de área de cobertura */}
            {coordenadasCirculo && (
              <Circle
                center={[coordenadasCirculo.lat, coordenadasCirculo.lng]}
                radius={radio}
                pathOptions={{
                  color: 'blue',
                  fillColor: 'lightblue',
                  fillOpacity: 0.3,
                  weight: 2
                }}
              />
            )}
            
            {/* Marcador del centro seleccionado */}
            {centroSeleccionado && (
              <Marker
                position={[centroSeleccionado.lat, centroSeleccionado.lng]}
                icon={L.divIcon({
                  className: 'custom-center-marker',
                  html: `
                    <div style="
                      background-color: red;
                      border: 2px solid white;
                      border-radius: 50%;
                      width: 20px;
                      height: 20px;
                      box-shadow: 0 2px 4px rgba(0,0,0,0.3);
                    "></div>
                  `,
                  iconSize: [20, 20],
                  iconAnchor: [10, 10]
                })}
              />
            )}
          </MapContainer>
        </div>
      </div>
    </div>
  );
};

export default ConfigMap;