from neo4j import GraphDatabase
import folium
import config
# Configuración de la conexión a Neo4j
uri = config.URI
user = config.USER
password = config.PASSWORD


driver = GraphDatabase.driver(uri, auth=(user, password))

def obtener_caminos_yens(k=3, source=4801, target=61):
    query = """
    CALL gds.shortestPath.yens.stream('mapa-logistico', {
      sourceNode: $source,
      targetNode: $target,
      k: $k,
      relationshipWeightProperty: 'length'
    })
    YIELD index, nodeIds
    RETURN index, 
      [nodeId IN nodeIds | 
        {id: nodeId, lat: gds.util.asNode(nodeId).lat, lon: gds.util.asNode(nodeId).lon}
      ] AS camino
    ORDER BY index
    """
    with driver.session() as session:
        result = session.run(query, source=source, target=target, k=k)
        return [(record["index"], record["camino"]) for record in result]

# Obtener los 3 mejores caminos
caminos = obtener_caminos_yens(k=3)

# Crear el mapa centrado en el primer nodo del primer camino
primer_camino = caminos[0][1]
centro = primer_camino[0]
mapa = folium.Map(location=[centro["lat"], centro["lon"]], zoom_start=14)

# Colores para diferenciar cada camino
colores = ["blue", "green", "red"]

# Dibujar cada camino y sus marcadores
for idx, camino in caminos:
    coords = [(n["lat"], n["lon"]) for n in camino]
    folium.PolyLine(coords, color=colores[idx], weight=4.5, opacity=0.8).add_to(mapa)
    # Marcador de inicio y fin
    folium.Marker(location=coords[0], popup=f"Inicio {idx+1}", icon=folium.Icon(color="green")).add_to(mapa)
    folium.Marker(location=coords[-1], popup=f"Fin {idx+1}", icon=folium.Icon(color="red")).add_to(mapa)

# Guardar resultado
mapa.save("ruta_yens_3caminos.html")

print("Mapa generado en ruta_yens_3caminos.html")
