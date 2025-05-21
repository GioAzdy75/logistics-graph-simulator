import networkx as nx
import random
import numpy as np

def initialize_pheromones(graph, initial_pheromone=1.0):
    for u, v in graph.edges():
        graph[u][v]['pheromone'] = initial_pheromone
    print(f"[DEBUG] Feromonas inicializadas en {initial_pheromone}")

def evaluate_path(graph, path):
    total = 0
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        if graph.has_edge(u, v):
            total += graph[u][v].get('length', 1e6)
        else:
            print(f"[DEBUG] Camino inválido: {u} -> {v} no existe")
            return float('inf')
    print(f"[DEBUG] Camino evaluado: {path} | Costo: {total}")
    return total

def select_next_node(graph, current, visited, end, alpha, beta):
    neighbors = [n for n in graph.neighbors(current) if n not in visited]
    if not neighbors:
        print(f"[DEBUG] Sin vecinos disponibles desde {current}")
        return None

    pheromones = []
    heuristics = []
    for n in neighbors:
        pheromone = graph[current][n]['pheromone']
        length = graph[current][n].get('length', 1e6)
        pheromones.append(pheromone ** alpha)
        heuristics.append((1.0 / length) ** beta if length > 0 else 0)

    probs = np.array(pheromones) * np.array(heuristics)
    if probs.sum() == 0:
        print(f"[DEBUG] Probabilidades nulas desde {current}")
        return None
    probs = probs / probs.sum()
    next_node = np.random.choice(neighbors, p=probs)
    print(f"[DEBUG] Desde {current}, vecinos: {neighbors}, seleccionado: {next_node}")
    return next_node

def construct_ant_path(graph, start, end, alpha, beta):
    path = [start]
    visited = set([start])
    current = start

    while current != end:
        next_node = select_next_node(graph, current, visited, end, alpha, beta)
        if next_node is None:
            try:
                sp = nx.shortest_path(graph, current, end, weight='length')
                for n in sp[1:]:
                    if n in visited:
                        print(f"[DEBUG] Ciclo detectado en shortest_path desde {current} a {end}")
                        return []
                    path.append(n)
                print(f"[DEBUG] Camino completado con shortest_path: {path}")
                return path
            except Exception as e:
                print(f"[DEBUG] No se pudo completar camino con shortest_path: {e}")
                return []
        path.append(next_node)
        visited.add(next_node)
        current = next_node
    print(f"[DEBUG] Camino construido por hormiga: {path}")
    return path

def evaporate_pheromones(graph, evaporation_rate):
    for u, v in graph.edges():
        old = graph[u][v]['pheromone']
        graph[u][v]['pheromone'] *= (1 - evaporation_rate)
        graph[u][v]['pheromone'] = max(0.01, graph[u][v]['pheromone'])
        print(f"[DEBUG] Evaporación: ({u},{v}) {old:.4f} -> {graph[u][v]['pheromone']:.4f}")

def reinforce_pheromones(graph, path, score, Q=1.0):
    if not path or score == float('inf'):
        print(f"[DEBUG] No se refuerza feromona, camino inválido.")
        return
    delta = Q / score if score > 0 else Q
    for i in range(len(path) - 1):
        u, v = path[i], path[i+1]
        old = graph[u][v]['pheromone']
        graph[u][v]['pheromone'] += delta
        print(f"[DEBUG] Refuerzo: ({u},{v}) {old:.4f} -> {graph[u][v]['pheromone']:.4f} (delta={delta:.4f})")

def moaco(
    graph,
    start_node=None,
    end_nodes=None,
    num_ants=5,
    num_iterations=20,
    alpha=1.0,
    beta=2.0,
    evaporation_rate=0.1,
    initial_pheromone=1.0
):
    nodes = list(graph.nodes())
    if start_node is None:
        start_node = random.choice(nodes)
    if end_nodes is None:
        end_nodes = [n for n in nodes if n != start_node]

    print(f"[DEBUG] Nodo de inicio: {start_node}")
    print(f"[DEBUG] Nodos destino: {end_nodes}")

    initialize_pheromones(graph, initial_pheromone)
    best_paths_per_client = {}

    for end_node in end_nodes:
        best_path = []
        best_score = float('inf')
        print(f"[DEBUG] Buscando camino a {end_node}")

        for it in range(num_iterations):
            all_paths = []
            print(f"[DEBUG] Iteración {it+1}/{num_iterations}")
            for ant in range(num_ants):
                path = construct_ant_path(graph, start_node, end_node, alpha, beta)
                score = evaluate_path(graph, path) if path else float('inf')
                print(f"[DEBUG] Hormiga {ant+1}: Camino: {path} | Score: {score}")
                all_paths.append((path, score))

            evaporate_pheromones(graph, evaporation_rate)

            valid_paths = [p for p in all_paths if p[0] and p[1] < float('inf')]
            if valid_paths:
                best_iter_path, best_iter_score = min(valid_paths, key=lambda x: x[1])
                reinforce_pheromones(graph, best_iter_path, best_iter_score)
                if best_iter_score < best_score:
                    best_score = best_iter_score
                    best_path = best_iter_path
                    print(f"[DEBUG] Nuevo mejor camino a {end_node}: {best_path} | Score: {best_score}")

        if best_path:
            best_paths_per_client[end_node] = (best_path, best_score)
            print(f"[DEBUG] Mejor camino final a {end_node}: {best_path} | Score: {best_score}")
        else:
            best_paths_per_client[end_node] = ([], float('inf'))
            print(f"[DEBUG] No se encontró camino válido a {end_node}")

    return best_paths_per_client

def reformat_path(path_tuple):
    path = path_tuple[0]
    print(f"[DEBUG] Reformateando camino: {path}")
    return [(path[i], path[i+1]) for i in range(len(path)-1)] if path else []