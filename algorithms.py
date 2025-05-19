import networkx as nx
import random

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

def moaco(graph, start_nodes=None, end_nodes=None, num_ants=5, num_iterations=30, alpha=1, beta=2, evaporation_rate=0.1):
    """
    MOACO adaptado para devolver el mejor camino desde cualquier heladería a cada cliente.
    :return: Diccionario {cliente: (camino, puntuación)}
    """

    nodes = list(graph.nodes())
    if start_nodes is None:
        start_nodes = random.sample(nodes, min(3, len(nodes)))
    if end_nodes is None:
        # Evitar que los end_nodes estén en start_nodes
        posibles_end = [n for n in nodes if n not in start_nodes]
        if len(posibles_end) < 10:
            end_nodes = posibles_end
        else:
            end_nodes = random.sample(posibles_end, 10)

    initialize_pheromone(graph)
    best_paths_per_client = {}

    for end_node in end_nodes:
        best_paths = []
        for _ in range(num_iterations):
            paths = []
            for _ in range(num_ants):
                start_node = random.choice(start_nodes)
                path = [start_node]
                current_node = start_node
                while current_node != end_node:
                    neighbors = list(graph.neighbors(current_node))
                    if not neighbors:
                        # No hay vecinos, camino inválido
                        path = []  # O puedes dejar el path hasta aquí
                        break
                    probabilities = [
                        calculate_transition_probability(graph, current_node, neighbor, alpha, beta)
                        for neighbor in neighbors
                    ]
                    next_node = random.choices(neighbors, weights=probabilities, k=1)[0]
                    path.append(next_node)
                    current_node = next_node
                score = evaluate_path(graph, path)
                paths.append((path, score))
            update_pheromones(graph, paths, evaporation_rate)
            best_paths.append(min(paths, key=lambda x: x[1]))
        # Mejor camino para este cliente
        best_paths_per_client[end_node] = min(best_paths, key=lambda x: x[1])

    return best_paths_per_client

def reformat_path(path):
    new_path = []
    for i in range(len(path[0])-1):
        new_path.append((path[0][i], path[0][i+1]))
    return new_path
