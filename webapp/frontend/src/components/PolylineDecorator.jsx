// src/components/PolylineDecorator.jsx
import { useEffect } from "react";
import { useMap } from "react-leaflet";
import L from "leaflet";

export default function PolylineDecorator({ positions }) {
  const map = useMap();

  useEffect(() => {
    if (!positions || positions.length < 2) return;

    const decorator = L.polylineDecorator(positions, {
      patterns: [
        {
          offset: 10,
          repeat: 50,
          symbol: L.Symbol.arrowHead({
            pixelSize: 10,
            polygon: false,
            pathOptions: { color: "blue", weight: 2 },
          }),
        },
      ],
    });

    decorator.addTo(map);

    return () => {
      decorator.removeFrom(map);
    };
  }, [map, positions]);

  return null;
}
