import numpy as np

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


def compute_distance_matrix(driver,poi_ids):
    CY_DIJKSTRA = """
    MATCH (start:Intersection) WHERE id(start) = $source
    CALL gds.shortestPath.dijkstra.stream('mapa-logistico', {
    sourceNode: id(start),
    targetNodes: $targets,
    relationshipWeightProperty: 'length'
    })
    YIELD targetNode, totalCost
    RETURN targetNode, totalCost
    """
    n = len(poi_ids)
    # Crear matriz inicial infinita
    dist = np.full((n, n), np.inf)
    np.fill_diagonal(dist, 0.0)
    node_idx = build_node_index(poi_ids)

    with driver.session() as session:
        for src_id in poi_ids:
            result = session.run(CY_DIJKSTRA, source=src_id, targets=poi_ids)
            i = node_idx[src_id]
            for record in result:
                tgt_id = record["targetNode"]
                cost = record["totalCost"]
                if tgt_id in node_idx:
                    j = node_idx[tgt_id]
                    dist[i, j] = cost
    return dist