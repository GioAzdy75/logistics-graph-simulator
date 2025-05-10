import numpy as np
import pandas as pd
import config
from neo4j import GraphDatabase


import graph_map



from consults import get_poi_ids,get_nodes_by_ids, extract_graph_data

URI      = config.URI # Default : "bolt://localhost:7687"
USER     = config.USER # Default : "neo4j"
PASSWORD = config.PASSWORD #

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

#Nodos de Interes
#ids_nodos = [4801, 187, 17258, 61] # Source Ids
#ids_nodos = [1135846205, 480124288, 6064229614, 287055452]
#Calculamos las distancias
""" 
dist_matrix, paths = compute_distance_matrix_dijkstra(driver, ids_nodos)
print("Matriz de distancias (Dijkstra):")
print(dist_matrix)


# Guardar la matriz
np.save("dist_matrix.npy", dist_matrix)
print("Matriz de distancias guardada como dist_matrix.npy")


#Imprimir todos los caminos
#print(paths[(4801,187)])
print(paths)
graph_map.create_graph_map_from_paths(paths)
 """

#Ejecutamos Optimizacion
###Se ejectuario el algoritmo de optimizacion y nos devolveria el orden de busqueda del nodo ej [node1,node3,node2,node4]
# luego con eso hay que crear una lista de la forma  [(node1,node3),(node3,node2),...] 
graph = extract_graph_data(driver)

from algorithms import moaco, reformat_path

optimal_path = moaco(graph)[0]



path_key = (optimal_path[0], optimal_path[-1])

path_nodes = get_nodes_by_ids(driver, optimal_path)

new_path = {path_key: path_nodes}

# Crear el mapa con el nuevo camino
graph_map.create_graph_map_single_color(new_path)




driver.close()