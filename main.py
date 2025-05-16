import config
from neo4j import GraphDatabase
import graph_map
from consults import get_nodes_by_ids, extract_graph_data

URI      = config.URI # Default : "bolt://localhost:7687"
USER     = config.USER # Default : "neo4j"
PASSWORD = config.PASSWORD #

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))


# Extraemos el grafo para operar internamente sobre el
graph = extract_graph_data(driver)

from algorithms import moaco

# Obtenemos la lista correspondiente al camino más optimo encontrado por MOACO
optimal_path = moaco(graph)[0]

"""Convertimos la lista obtenida en un diccionario con el formato:
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
path_key = (optimal_path[0], optimal_path[-1])
path_nodes = get_nodes_by_ids(driver, optimal_path)
new_path = {path_key: path_nodes}

# Crear el mapa con el nuevo camino
graph_map.create_graph_map_single_color(new_path)


driver.close()