import React from "react";
import { Link } from "react-router-dom";

export default function Introduction() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center p-8">
      <h1 className="text-3xl font-bold mb-4">Bienvenido al Sistema de Optimización de Rutas</h1>
      <p className="text-gray-700 max-w-xl mb-6">
        Esta aplicación te permite visualizar y gestionar rutas eficientes para tus puntos de distribución.
        Navegá con el menú lateral y explorá las funcionalidades disponibles.
      </p>
      <img
        src={"ejemplo"}
        alt="Mapa de rutas ilustrativo"
        className="max-w-md w-full rounded-lg shadow-lg mb-6"
      />
      <Link
        to="/locales"
        className="bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 transition"
      >
        Empezar ahora
      </Link>
    </div>
  );
}
