import csv
from services.neo4j_connection import Neo4jConnection

def importar_csv(conn: Neo4jConnection, nodes_path: str, edges_path: str):
    
    with open(nodes_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query = """
            MERGE (p:Point {id: $id})
            SET p.lat = toFloat($lat),
                p.lon = toFloat($lon),
                p.tipo = $tipo
            """
            conn.query(query, {
                'id': row['node_id:ID'],
                'lat': float(row['lat:float']),
                'lon': float(row['lon:float']),
                'tipo': row['tipo:string']
            })

    with open(edges_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            query = """
            MATCH (a:Point {id: $start_id}), (b:Point {id: $end_id})
            CREATE (a)-[:STREET {
                name: $name,
                length: toFloat($length),
                maxspeed: toInteger($maxspeed),
                weight: toFloat($weight)
            }]->(b)
            """
            conn.query(query, {
                'start_id': row[':START_ID'],
                'end_id': row[':END_ID'],
                'name': row['name:string'],
                'length': float(row['length:float']),
                'maxspeed': int(row['maxspeed:int']),
                'weight': float(row['weight:float'])
            })  

    return {"status": "ok", "mensaje": "Datos importados manualmente desde CSV"}