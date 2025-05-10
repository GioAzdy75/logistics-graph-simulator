import networkx as nx
import consults
import config
from neo4j import GraphDatabase
import random


""" 
URI      = config.URI # Default : "bolt://localhost:7687"
USER     = config.USER # Default : "neo4j"
PASSWORD = config.PASSWORD #

driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))

graph = consults.extract_graph_data(driver) """

def initialize_pheromone(G, base_pheromone=2.0):
    for _, _, data in G.edges(data=True):
        distance = data.get('length', 1e6)
        data['pheromone'] = base_pheromone / distance

def calculate_transition_probability(graph, current_node, next_node, alpha=1, beta=2):
    pheromone = graph[current_node][next_node]['pheromone']
    distance = graph[current_node][next_node]['length']
    
    # Heurística multiobjetivo (puedes ajustar los pesos)
    heuristic = (1.0 / distance) if distance > 0 else 0
    
    return (pheromone ** alpha) * (heuristic ** beta)

def update_pheromones(graph, paths, evaporation_rate=0.25):
    # Evaporación
    for u, v in graph.edges():
        graph[u][v]['pheromone'] *= (1 - evaporation_rate)
    
    # Incremento basado en las soluciones
    for path, score in paths:  # paths es una lista de (camino, puntuación)
        for i in range(len(path) - 1):
            u, v = path[i], path[i + 1]
            graph[u][v]['pheromone'] += 1 / score  # Incremento proporcional a la calidad

def evaluate_path(graph, path):
    total_length = 0
    for i in range(len(path) - 1):  # Iterar hasta el penúltimo nodo
        u, v = path[i], path[i + 1]
        if graph.has_edge(u, v):  # Verificar si la arista existe
            total_length += graph[u][v].get("length", float('inf'))  # Usar un valor predeterminado si no hay 'length'
        else:
            print(f"  Advertencia: No existe arista entre {u} y {v}.")
            return float('inf')  # Retornar un valor alto para indicar que el camino no es válido
    return total_length

def moaco(graph, num_ants=5, num_iterations=30, alpha=1, beta=2, evaporation_rate=0.1):
    initialize_pheromone(graph)
    print("Feromonas inicializadas.")
    start_node = random.choice(list(graph.nodes))
    end_node = random.choice(list(graph.nodes))
    print(f"Start node: {start_node}, End node: {end_node}")
    
    for iteration in range(num_iterations):
        print(f"\nIteración {iteration + 1}/{num_iterations}")
        paths = []
        
        # Paso 1: Cada hormiga construye un camino
        for ant in range(num_ants):
            print(f"  Hormiga {ant + 1}/{num_ants} construyendo camino...")
            path = []
            current_node = start_node  # Define un nodo inicial
            while current_node != end_node:
                neighbors = list(graph.neighbors(current_node))
                neighbors = [neighbor for neighbor in neighbors if neighbor not in path]
                if not neighbors:  # Si no hay vecinos, termina el bucle
                    print(f"    Nodo {current_node} no tiene vecinos. Termina el camino.")
                    break

                probabilities = [
                    calculate_transition_probability(graph, current_node, neighbor, alpha, beta)
                    for neighbor in neighbors
                ]
                
                if not any(probabilities):  # Si todas las probabilidades son 0, termina el bucle
                    print(f"    Todas las probabilidades son 0 en el nodo {current_node}. Termina el camino.")
                    break

                next_node = random.choices(neighbors, weights=probabilities, k=1)[0]
                path.append(next_node)
                current_node = next_node
            
            if path:
                score = evaluate_path(graph, path)
                if score == float('inf'):  # Si el camino no es válido
                    print(f"    Camino inválido: {path}")
                else:
                    #print(f"    Camino construido: {path} con puntuación: {score}")
                    paths.append((path, score))
            else:
                print(f"    Hormiga {ant + 1} no pudo construir un camino válido.")
        
        # Paso 2: Actualizar feromonas
        print("  Actualizando feromonas...")
        update_pheromones(graph, paths, evaporation_rate)
    
    # Retorna la mejor solución encontrada
    best_path = min(paths, key=lambda x: x[1], default=([], float('inf')))
    print(f"\nMejor camino encontrado: {best_path[0]} con puntuación: {best_path[1]}")
    return best_path

def reformat_path(path):
    new_path = []
    for i in range(len(path[0])-1):
        new_path.append((path[0][i], path[0][i+1]))
    return new_path
