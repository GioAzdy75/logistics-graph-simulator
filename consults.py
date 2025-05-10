import numpy as np
import networkx as nx

def get_poi_ids(driver):
    query = """
    MATCH (d:CentroDistribucion)-[:ACCESO_SALIDA]->(e:Esquina)
    WITH collect(id(e)) AS depotEsquinas

    MATCH (c:Cliente)<-[:ACCESO_ENTRADA]-(e2:Esquina)
    WITH depotEsquinas, collect(id(e2)) AS clienteEsquinas

    RETURN depotEsquinas + clienteEsquinas AS poiIds
    """
    with driver.session() as session:
        result = session.run(query).single()
        poi_ids = result["poiIds"]
        return list(dict.fromkeys(poi_ids))  # Elimina duplicados manteniendo orden


def build_node_index(poi_ids):
    return {nid: i for i, nid in enumerate(poi_ids)}

def get_nodes_by_ids(driver, ids):
    query = """
    UNWIND $ids AS node_id
    MATCH (n)
    WHERE n.id = node_id
    RETURN collect({
      id: n.id,
      lon: n.lon,
      lat: n.lat
    }) AS nodes
    """
    with driver.session() as session:
        result = session.run(query, ids=ids)
        return result.single()["nodes"]
""" 
def compute_distance_matrix_dijkstra(driver, poi_ids):
    ""
    Retorna una matriz de distancia minima evaluada por dijkstra entre los nodos, 
    y una un diccionario con los caminos que conforman las distancia entre los nodos antes planteados
    ""
    CY_DIJKSTRA_PATHS = ""
    MATCH (start:Intersection) WHERE id(start) = $source
    CALL gds.shortestPath.dijkstra.stream('mapa-logistico', {
      sourceNode: id(start),
      targetNodes: $targets,
      relationshipWeightProperty: 'length'
    })
    YIELD targetNode, totalCost, nodeIds
    UNWIND nodeIds AS nid
    WITH targetNode, totalCost, gds.util.asNode(nid) AS node
    RETURN 
      targetNode AS target_id,
      totalCost,
      collect({
        id: node.id,
        lon: node.lon,
        lat: node.lat
      }) AS path
    ""

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

    return dist, paths
 """

def extract_graph_data(driver):
    """
    Extrae los datos del grafo desde Neo4j y los convierte en un grafo de NetworkX.
    """
    G = nx.DiGraph()  # Cambia a nx.Graph() si el grafo no es dirigido

    with driver.session() as session:
        # Extraer nodos
        node_query = """
        MATCH (n)
        RETURN n.id AS node_id, labels(n) AS labels, properties(n) AS properties
        """
        node_results = session.run(node_query)
        for record in node_results:
            G.add_node(record["node_id"], labels=record["labels"], **record["properties"])

        # Extraer relaciones
        edge_query = """
        MATCH (n)-[r]->(m)
        RETURN n.id AS source_id, m.id AS target_id, type(r) AS type, properties(r) AS properties
        """
        edge_results = session.run(edge_query)
        for record in edge_results:
            G.add_edge(
                record["source_id"],
                record["target_id"],
                type=record["type"],
                **record["properties"]
            )

    return G