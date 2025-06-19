import { useNavigate } from "react-router-dom";

export default function Introduction() {
  const navigate = useNavigate();
  return (
    <section className="ml-64 p-6">
      <h2 className="text-3xl font-bold mb-4">Introducción</h2>
      <p className="text-lg text-gray-700">
        Este sistema permite ubicar puntos en el mapa como locales o centros de distribución
        y calcular rutas óptimas entre ellos utilizando algoritmos de optimización.
        Los datos de los puntos provendrán de una API externa.
      </p>
      <button
        className="mt-8 bg-blue-600 text-white px-6 py-2 rounded hover:bg-blue-700 font-semibold"
        onClick={() => navigate("/login")}
      >
        Iniciar sesión
      </button>
    </section>
  );
}
