from neo4j import GraphDatabase
import folium
import config


from itertools import cycle


def create_graph_map_from_paths(paths):
    """input: es un diccionario con los caminos entre los nodos con el formato ejemplo:
    {(nodo_1,nodo_2) : [{"id": 4801, "lon": -68.8205003, "lat": -32.9040337}
                        {"id": 4792, "lon": -68.8205776, "lat": -32.9046553},
                        {"id": 4780, "lon": -68.8206100, "lat": -32.9051000},
                        ...
                       ],
     (nodo_5,nodo_9) : [...],
     (nodo_3,nodo_7) : [...],
     ...
    }
    
    """
    if not paths:
        print("No hay caminos para graficar.")
        return

    # Usar el primer nodo del primer camino para centrar el mapa
    primer_camino = next(iter(paths.values()))
    centro = primer_camino[0]
    mapa = folium.Map(location=[centro["lat"], centro["lon"]], zoom_start=14)

    # Colores ciclando si hay muchos caminos
    colores = cycle(["blue", "green", "red", "orange", "purple", "brown", "black", "pink", "gray"])

    for idx, ((src_id, tgt_id), camino) in enumerate(paths.items()):
        coords = [(n["lat"], n["lon"]) for n in camino]
        color = next(colores)

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

    # Guardar resultado
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