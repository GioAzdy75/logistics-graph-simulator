
import numpy as np
import pandas as pd
import config
from neo4j import GraphDatabase


import graph_map



from consults import get_poi_ids,compute_distance_matrix_dijkstra

URI      = config.URI # Default : "bolt://localhost:7687"
USER     = config.USER # Default : "neo4j"
PASSWORD = config.PASSWORD #

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


lista = [6516, 18810, 18811, 18809, 18806]

def get_node_coordinates(driver, node_ids, start_id, end_id):
    query = """
    MATCH (n)
    WHERE id(n) IN $ids
    RETURN id(n) AS internal_id, n.id AS osm_id, n.lon AS lon, n.lat AS lat
    """
    with driver.session() as session:
        result = session.run(query, ids=node_ids)
        nodes = result.data()

    # Ordenamos los nodos en el orden dado
    ordered_nodes = [n for node_id in node_ids for n in nodes if n["internal_id"] == node_id]

    # Creamos la estructura del diccionario
    path_dict = {
        (start_id, end_id): [
            {"id": int(n["osm_id"]), "lon": n["lon"], "lat": n["lat"]}
            for n in ordered_nodes
        ]
    }

    return path_dict


# Ejemplo de uso:
node_ids = [6516, 18810, 18811, 18809, 18806]
start_id = 6516
end_id = 18806

data = get_node_coordinates(driver, node_ids, start_id, end_id)
print(data)

import graph_map
graph_map.create_graph_map_single_color(data)