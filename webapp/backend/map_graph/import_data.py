from services.neo4j_connection import Neo4jConnection

def importar_csv(conn: Neo4jConnection, nodes_path: str, edges_path: str, borrar_antes=True):
    if borrar_antes:
        conn.query("MATCH (n) DETACH DELETE n")

    query_nodes = f"""
    LOAD CSV WITH HEADERS FROM 'file:///{nodes_path}' AS row
    CREATE (:Point {{
        id: row.`node_id:ID`,
        lat: toFloat(row.`lat:float`),
        lon: toFloat(row.`lon:float`),
        tipo: row.`tipo:string`
    }})
    """

    query_edges = f"""
    LOAD CSV WITH HEADERS FROM 'file:///{edges_path}' AS row
    MATCH (a:Point {{id: row.`:START_ID`}}), (b:Point {{id: row.`:END_ID`}})
    CREATE (a)-[:STREET {{
        name: row.`name:string`,
        length: toFloat(row.`length:float`),
        maxspeed: toInteger(row.`maxspeed:int`),
        weight: toFloat(row.`weight:float`)
    }}]->(b)
    """

    conn.query(query_nodes)
    conn.query(query_edges)

    return {"status": "ok", "mensaje": "Mapa importado correctamente desde CSV"}
