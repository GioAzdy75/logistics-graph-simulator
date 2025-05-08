import numpy as np
import pandas as pd
import config
from neo4j import GraphDatabase


from consults import get_poi_ids,compute_distance_matrix

URI      = config.URI # Default : "bolt://localhost:7687"
USER     = config.USER # Default : "neo4j"
PASSWORD = config.PASSWORD #

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

#Nodos de Interes
#ids_nodos = ["480124288", "187", "17258", "61", "137", "258", "94", "185"]
ids_nodos = [4801, 187, 17258, 61, 137, 258, 94, 185]
ids_nodos = [4801, 187, 17258, 61]

# Obtenemos los poi ids
#poi_ids = get_poi_ids(driver)
#n = len(poi_ids)
#print(f"POIs encontrados: {n}  ->  {poi_ids}")

#Calculamos las distancias
dist_matrix = compute_distance_matrix(driver, ids_nodos)
print("Matriz de distancias (Dijkstra):")
print(dist_matrix)

# Guardar la matriz
np.save("dist_matrix.npy", dist_matrix)
print("Matriz de distancias guardada como dist_matrix.npy")

driver.close()