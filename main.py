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

#Nodos de Interes
ids_nodos = [4801, 187, 17258, 61] # Source Ids
#ids_nodos = [1135846205, 480124288, 6064229614, 287055452]
#Calculamos las distancias
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


# {
#  (19488,15418) = [{"id": 149488, "lon": -68.8205003, "lat": -32.9040337}
#                        {"id": 15408, "lon": -68.8205776, "lat": -32.9046553},
#                        {"id": 15407, "lon": -68.8206100, "lat": -32.9051000},
#                        ...
#                    ],
# 
# }  

#Ejecutamos Optimizacion
###Se ejectuario el algoritmo de optimizacion y nos devolveria el orden de busqueda del nodo ej [node1,node3,node2,node4]
# luego con eso hay que crear una lista de la forma  [(node1,node3),(node3,node2),...] 
optimal_path = [(4801, 61), (61, 17258), (17258, 187), (187, 4801)] #este es el resultado despues de efectuarlo

#Nuevo camino , filtra del diccionario paths y crea uno nuevo con new_paths solo con los caminos finales que usaremos
new_path = {}
for optimal in optimal_path:
    new_path[optimal] = paths[optimal]

graph_map.create_graph_map_single_color(new_path)




driver.close()