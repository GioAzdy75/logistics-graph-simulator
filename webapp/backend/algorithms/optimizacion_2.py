from collections import defaultdict
import numpy as np
import random

"""
Este algoritmo en especifico primero corre un preprocesado en la base de Neo4j que consiste en calcular un k-caminos yens entre todos los nodos (clientes)
y nodos (centro de distribucion), 

##con ello se crea una matriz de distancias que luego se usara para correr ACO para optimizar el orden de visita.
"""


def obtener_caminos_yens(driver,k=3, source=4801, target=61):
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
    


def euclidean_distance(a, b):
    return ((a['lat'] - b['lat'])**2 + (a['lon'] - b['lon'])**2)**0.5

def procesar_caminos_yens(poi_origen, poi_destino, caminos_yens):
    dist = defaultdict(lambda: defaultdict(list))
    pheromone = defaultdict(lambda: defaultdict(list))
    paths = defaultdict(lambda: defaultdict(list))

    for (index, camino) in caminos_yens:
        costo = 0.0
        for i in range(len(camino) - 1):
            costo += euclidean_distance(camino[i], camino[i+1])

        i = poi_origen
        j = poi_destino
        dist[i][j].append(costo)
        pheromone[i][j].append(1.0)  # inicialización
        paths[i][j].append(camino)

    return dist, pheromone, paths


class ACO:
    def __init__(self, dist, pheromone, alpha=1.0, beta=2.0, evaporation=0.5, q=100.0):
        """
        dist: matriz (n x n) donde cada celda dist[i][j] es una lista de hasta k costos
        pheromone: misma estructura que dist, pheromone[i][j][c] representa la feromona del camino c entre i y j
        """
        self.dist = dist
        self.pheromone = pheromone
        self.n = len(dist)
        self.alpha = alpha
        self.beta = beta
        self.evaporation = evaporation
        self.q = q
        self.best_route = None
        self.best_cost = np.inf
        self.log_detallado = []

    def _calcular_probabilidades(self, actual, no_visitados):
        """Devuelve una lista de tuplas (j, c, probabilidad)"""
        numeradores = []
        transiciones = []

        for j in no_visitados:
            for c in range(len(self.dist[actual][j])):
                tau = self.pheromone[actual][j][c]
                eta = 1.0 / self.dist[actual][j][c]
                valor = (tau ** self.alpha) * (eta ** self.beta)
                numeradores.append(valor)
                transiciones.append((j, c))

        total = sum(numeradores)
        probabilidades = [(j, c, v / total) for (j, c), v in zip(transiciones, numeradores)]
        return probabilidades

    def _elegir_siguiente(self, actual, no_visitados):
        """Elige el siguiente nodo y camino según las probabilidades"""
        probs = self._calcular_probabilidades(actual, no_visitados)
        r = random.random()
        acumulado = 0.0
        for j, c, p in probs:
            acumulado += p
            if r <= acumulado:
                return j, c
        return probs[-1][0], probs[-1][1]  # por fallback

    def _construir_solucion(self):
        """Construye una solución recorriendo todos los nodos una vez"""
        camino = []
        costo_total = 0.0
        no_visitados = list(range(self.n))
        actual = random.choice(no_visitados)
        inicio = actual
        no_visitados.remove(actual)

        while no_visitados:
            siguiente, camino_idx = self._elegir_siguiente(actual, no_visitados)
            camino.append((actual, siguiente, camino_idx))
            costo_total += self.dist[actual][siguiente][camino_idx]
            actual = siguiente
            no_visitados.remove(actual)

        # Volver al inicio
        if inicio in range(self.n):
            if len(self.dist[actual][inicio]) > 0:
                camino.append((actual, inicio, 0))
                costo_total += self.dist[actual][inicio][0]

        return camino, costo_total

    def _actualizar_feromonas(self, soluciones):
        """Evaporación y refuerzo de feromonas"""
        for i in range(self.n):
            for j in range(self.n):
                for c in range(len(self.pheromone[i][j])):
                    self.pheromone[i][j][c] *= (1 - self.evaporation)

        for camino, costo in soluciones:
            for i, j, c in camino:
                self.pheromone[i][j][c] += self.q / costo

    def run(self, iteraciones=100, n_hormigas=10):
        for _ in range(iteraciones):
            soluciones = []
            for _ in range(n_hormigas):
                camino, costo = self._construir_solucion()
                soluciones.append((camino, costo))
                if costo < self.best_cost:
                    self.best_cost = costo
                    self.best_route = camino
            self._actualizar_feromonas(soluciones)

        return self.best_route, self.best_cost



def serializar_camino(mejor_ruta, paths, poi_ids):
    """
    mejor_ruta: lista de tuplas (i, j, c) con índice del camino usado
    paths: matriz paths[i][j][c] = lista de nodos (con lat/lon)
    poi_ids: lista con los ids reales de los nodos (mapeo de índice a id)
    """
    rutas_serializables = {}

    for i, j, c in mejor_ruta:
        id_origen = poi_ids[i]
        id_destino = poi_ids[j]
        tramo = paths[i][j][c]

        rutas_serializables[f"{id_origen}-{id_destino}"] = tramo

    return rutas_serializables


def ejecutarOptimizacion(driver):
    poi_ids = [4801, 187, 17258, 61, 13, 21, 831, 999, 666, 10, 121, 123, 354] # Source Ids
    # Inicialización
    n = len(poi_ids)
    dist = [[[] for _ in range(n)] for _ in range(n)]
    pheromone = [[[] for _ in range(n)] for _ in range(n)]
    paths = [[[] for _ in range(n)] for _ in range(n)]
    k = 3 #Numero de caminos por cada nodo

    # Para cada par (i, j)
    for i, src_id in enumerate(poi_ids):
        for j, tgt_id in enumerate(poi_ids):
            if src_id == tgt_id:
                continue
            caminos_yens = obtener_caminos_yens(driver, k, src_id, tgt_id)
            dist_ij, pheromone_ij, paths_ij = procesar_caminos_yens(i, j, caminos_yens)

            dist[i][j] = dist_ij[i][j]
            pheromone[i][j] = pheromone_ij[i][j]
            paths[i][j] = paths_ij[i][j]

    aco = ACO(dist, pheromone, alpha=1.0, beta=2.0, evaporation=0.3, q=100.0)

    mejor_camino, mejor_costo = aco.run(iteraciones=30, n_hormigas=10)
    print(mejor_costo)
    rutas_serializadas = serializar_camino(mejor_camino,paths,poi_ids)

    return rutas_serializadas