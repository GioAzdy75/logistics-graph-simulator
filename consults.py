import networkx as nx

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

def extract_graph_data(driver):
    """
    Extrae los datos del grafo desde Neo4j y los convierte en un grafo de NetworkX.
    """
    G = nx.DiGraph()

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