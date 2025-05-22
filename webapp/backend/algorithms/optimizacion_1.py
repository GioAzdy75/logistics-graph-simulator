
import numpy as np
import random
import pandas as pd

"""
Este algoritmo en especifico primero corre un preprocesado en la base de Neo4j que consiste en calcular un dijkstra entre todos los nodos (clientes)
y nodos (centro de distribucion), con ello se crea una matriz de distancias que luego se usara para correr ACO para optimizar el orden de visita.
"""


class ACO:
    def __init__(self, dist, tau, alpha=1.0, beta=2.0, evaporation=0.5, q=100.0):
        self.dist = dist
        self.tau = tau
        self.n = dist.shape[0]
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q
        self.best_route = None
        self.best_cost = np.inf

    def _probabilidad(self, i, no_visitados):
        attractiveness = []
        for j in no_visitados:
            pheromone = self.tau[i, j] ** self.alpha
            heuristic = (1.0 / self.dist[i, j]) ** self.beta if self.dist[i, j] > 0 else 0
            attractiveness.append(pheromone * heuristic)
        total = sum(attractiveness)
        if total == 0:
            probs = [1/len(no_visitados)] * len(no_visitados)
        else:
            probs = [a/total for a in attractiveness]
        return probs

    def _construir_ruta(self):
        ruta = [0]
        no_visitados = set(range(1, self.n))

        while no_visitados:
            i = ruta[-1]
            no_vis = list(no_visitados)
            probs = self._probabilidad(i, no_vis)
            siguiente = random.choices(no_vis, weights=probs, k=1)[0]
            ruta.append(siguiente)
            no_visitados.remove(siguiente)

        ruta.append(0)
        return ruta

    def _costo_ruta(self, ruta):
        return sum(self.dist[ruta[i], ruta[i+1]] for i in range(len(ruta) - 1))

    def _evaporar(self):
        self.tau *= (1 - self.evaporation)

    def _depositar_feromonas(self, rutas, costos):
        for ruta, cost in zip(rutas, costos):
            feromona = self.q / cost
            for i in range(len(ruta) - 1):
                self.tau[ruta[i], ruta[i+1]] += feromona

    def correr(self, n_ants=10, n_iteraciones=100):
        for it in range(n_iteraciones):
            rutas = []
            costos = []

            for _ in range(n_ants):
                ruta = self._construir_ruta()
                costo = self._costo_ruta(ruta)
                rutas.append(ruta)
                costos.append(costo)

                if costo < self.best_cost:
                    self.best_route = ruta
                    self.best_cost = costo

            self._evaporar()
            self._depositar_feromonas(rutas, costos)

            #print(f"Iteración {it+1}: Mejor costo hasta ahora: {self.best_cost:.2f}")

        return self.best_route, self.best_cost




def build_node_index(poi_ids):
    return {nid: i for i, nid in enumerate(poi_ids)}

def compute_distance_matrix_dijkstra(driver, poi_ids):
    """
    Retorna una matriz de distancia minima evaluada por dijkstra entre los nodos, 
    y una un diccionario con los caminos que conforman las distancia entre los nodos antes planteados
    """

    CY_DIJKSTRA_PATHS = """
    MATCH (start:Point {id: $source})
    WITH id(start) AS sourceNodeId
    MATCH (target:Point)
    WHERE target.id IN $targets
    WITH sourceNodeId, collect(id(target)) AS targetNodeIds
    CALL gds.shortestPath.dijkstra.stream('mapa-logistico', {
    sourceNode: sourceNodeId,
    targetNodes: targetNodeIds,
    relationshipWeightProperty: 'length'
    })
    YIELD targetNode, totalCost, nodeIds
    UNWIND nodeIds AS nid
    WITH targetNode, totalCost, gds.util.asNode(nid) AS node
    RETURN 
    gds.util.asNode(targetNode).id AS target_id,
    totalCost,
    collect({
        id: node.id,
        lon: node.lon,
        lat: node.lat
    }) AS path
    """
    n = len(poi_ids)
    dist = np.full((n, n), np.inf)
    np.fill_diagonal(dist, 0.0)
    node_idx = build_node_index(poi_ids)
    paths = {}

    with driver.session() as session:
        for src_id in poi_ids:
            result = session.run(CY_DIJKSTRA_PATHS, source=src_id, targets=poi_ids)
            i = node_idx[src_id]
            for record in result:
                tgt_id = record["target_id"]
                cost = record["totalCost"]
                path = record["path"]

                if tgt_id in node_idx:
                    j = node_idx[tgt_id]
                    dist[i, j] = cost
                    paths[(src_id, tgt_id)] = path

    print("Matriz de distancias:")
    print(dist)
    print("Caminos calculados:")
    for k, v in paths.items():
        print(f"{k[0]} -> {k[1]} | {len(v)} nodos | camino: {[p['id'] for p in v]}")

    return dist, paths

def crear_matriz_feromonas(dist):
    n = dist.shape[0]
    # Definir parámetros
    umbral_cercania = 300.0  # metros
    tau_cercano = 1.0         # feromonas para caminos cortos
    tau_lejano = 0.1          # feromonas para caminos largos
    #Crea la matriz de feromonas
    tau = np.full((n, n), tau_lejano)
    # Asignar feromonas mayores en caminos cercanos
    for i in range(n):
        for j in range(n):
            if i != j and dist[i, j] < umbral_cercania:
                tau[i, j] = tau_cercano

    return tau


def ejecutarOptimizacion(driver,puntos):
    lista_nodos = [p["id"] for p in puntos]
    print(lista_nodos)
    #Creamos matriz distancia con dijkstra entre los nodos
    dist_matrix, paths = compute_distance_matrix_dijkstra(driver,lista_nodos)
    #Guardamos los calculos hechos
    np.save("dist_matrix.npy", dist_matrix)

    #Ejecutamos optimizacion
    ##Creamos la matriz de feromonas
    tau = crear_matriz_feromonas(dist_matrix)
    print("Matriz de distancias:")
    for row in dist_matrix:
        print(row)
    ##Inicializamos ACO
    aco = ACO(dist_matrix,tau)
    mejor_ruta, mejor_costo = aco.correr(n_ants=10,n_iteraciones=30)
    
    #Parsear la mejor ruta
    head = lista_nodos[mejor_ruta[0]]
    optimal_path = []
    for m in mejor_ruta[1:]:
        second = lista_nodos[m]
        optimal_path.append((head,second))
        head = second

    #Nuevo camino , filtra del diccionario paths y crea uno nuevo con new_paths solo con los caminos finales que usaremos
    new_path = {}
    for optimal in optimal_path:
        new_path[optimal] = paths[optimal]

    rutas_serializables = {
        f"{origen}-{destino}": path for (origen, destino), path in new_path.items()
    }

    return rutas_serializables