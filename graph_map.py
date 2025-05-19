import folium

from itertools import cycle


def create_graph_map_from_paths(list_of_paths):
    """
    Recibe una lista de diccionarios, cada uno con caminos entre nodos en el formato:
    {
        (nodo_1, nodo_2): [ {id, lon, lat}, ... ],
        (nodo_3, nodo_4): [ ... ],
        ...
    }
    Grafica cada diccionario como un camino en el mapa, usando un color diferente para cada uno.
    """
    if not list_of_paths or not any(list_of_paths):
        print("No hay caminos para graficar.")
        return

    # Encontrar el primer nodo para centrar el mapa
    for paths in list_of_paths:
        if paths:
            primer_camino = next(iter(paths.values()))
            if primer_camino:
                centro = primer_camino[0]
                break
    else:
        print("No hay caminos válidos para graficar.")
        return

    import folium
    from itertools import cycle

    mapa = folium.Map(location=[centro["lat"], centro["lon"]], zoom_start=14)
    colores = cycle(["blue", "green", "red", "orange", "purple", "brown", "black", "pink", "gray"])

    for idx, paths in enumerate(list_of_paths):
        color = next(colores)
        for (src_id, tgt_id), camino in paths.items():
            coords = [(n["lat"], n["lon"]) for n in camino]
            # Dibujar la línea del camino
            folium.PolyLine(coords, color=color, weight=4.5, opacity=0.8).add_to(mapa)
            # Marcadores de inicio y fin
            folium.Marker(
                location=coords[0],
                popup=f"Inicio {src_id}",
                icon=folium.Icon(color="green")
            ).add_to(mapa)
            folium.Marker(
                location=coords[-1],
                popup=f"Fin {tgt_id}",
                icon=folium.Icon(color="red")
            ).add_to(mapa)

    mapa.save("ruta_caminos.html")
    print("✅ Mapa generado: ruta_caminos.html")

def create_graph_map_single_color(paths, color="blue"):
    """Lo mismo que el anterio solo que asume todo los caminos que se le pase son parte de un unico camino por ende los pinta del mismo color"""
    if not paths:
        print("No hay caminos para graficar.")
        return

    # Usar el primer nodo del primer camino para centrar el mapa
    primer_camino = next(iter(paths.values()))
    centro = primer_camino[0]
    mapa = folium.Map(location=[centro["lat"], centro["lon"]], zoom_start=14)

    for (src_id, tgt_id), camino in paths.items():
        coords = [(n["lat"], n["lon"]) for n in camino]

        # Dibujar el camino con color único
        folium.PolyLine(coords, color=color, weight=4.5, opacity=0.9).add_to(mapa)

        # Marcadores de inicio y fin de cada segmento
        folium.Marker(
            location=coords[0],
            popup=f"Inicio {src_id}",
            icon=folium.Icon(color="green")
        ).add_to(mapa)

        folium.Marker(
            location=coords[-1],
            popup=f"Fin {tgt_id}",
            icon=folium.Icon(color="red")
        ).add_to(mapa)

    mapa.save("ruta_final_un_color.html")
    print("✅ Mapa generado con un solo color: ruta_final_un_color.html")