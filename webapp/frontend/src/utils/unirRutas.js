//Funcion para graficar la ruta
export const unirTramosRuta = (data) => {
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
