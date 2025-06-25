


from fastapi import HTTPException
from fastapi.responses import JSONResponse

from models.schemes import Coordenadas, InsercionRequest


def list_map_points(conn):
    """
    Devuelve todos los puntos de tipo Local o CentroDeDistribucion.
    """

    query = """
    MATCH (p:Point)
    WHERE p.tipo IN ['Local', 'CentroDeDistribucion']
    RETURN p.id AS id, p.name AS nombre, p.lat AS lat, p.lon AS lon, p.tipo AS tipo
    """
    with conn.driver.session() as session:
        result = session.run(query)
        puntos = [record.data() for record in result]
    return JSONResponse(content=puntos)

def delete_map_point(id:str ,conn):
    query = """
    MATCH (n:Point {id: $id})
    OPTIONAL MATCH (a)-[r1:STREET]->(n)-[r2:STREET]->(b)
    WITH n, a, b, r1, r2
    FOREACH (_ IN CASE WHEN a IS NOT NULL AND b IS NOT NULL THEN [1] ELSE [] END |
        CREATE (a)-[:STREET {
            name: r1.name,
            length: r1.length + r2.length,
            maxspeed: r1.maxspeed,
            weight: r1.weight + r2.weight
        }]->(b)
    )
    DETACH DELETE n
    RETURN 'ok' AS status
    """
    with conn.driver.session() as session:
        result = session.run(query, id=id)
        return result.single()

def obtener_tramo_cercano(coord: Coordenadas,conn):
    driver = conn.driver
    query = """
    WITH point({latitude: $lat, longitude: $lon}) AS input
    MATCH (n1:Point)
    WHERE point.distance(point({latitude: n1.lat, longitude: n1.lon}), input) < 1000
    WITH n1, input
    MATCH (n1)-[r:STREET]->(n2:Point)
    RETURN n1.id AS from_id, n1.lat AS from_lat, n1.lon AS from_lon,
           n2.id AS to_id, n2.lat AS to_lat, n2.lon AS to_lon,
           r.name AS calle,
           point.distance(point({latitude: n1.lat, longitude: n1.lon}), input) AS dist_from,
           point.distance(point({latitude: n2.lat, longitude: n2.lon}), input) AS dist_to
    ORDER BY dist_from + dist_to ASC
    LIMIT 1
    """
    with driver.session() as session:
        result = session.run(query, lat=coord.lat, lon=coord.lon)
        record = result.single()
        if record is None:
            raise HTTPException(status_code=404, detail="No se encontró un tramo cercano.")
        
        return {
            "calle": record["calle"],
            "from": {
                "id": record["from_id"],
                "lat": record["from_lat"],
                "lon": record["from_lon"],
                "distancia_m": record["dist_from"]
            },
            "to": {
                "id": record["to_id"],
                "lat": record["to_lat"],
                "lon": record["to_lon"],
                "distancia_m": record["dist_to"]
            }
        }
    

def insertar_nuevo_punto(data: InsercionRequest,conn):
    driver = conn.driver
    query = """
    WITH point({latitude: $lat, longitude: $lon}) AS nuevo_punto

    MATCH (a:Point {id: $from_id})-[r:STREET]->(b:Point {id: $to_id})
    
    WITH a, b, r, nuevo_punto,
         point({latitude: a.lat, longitude: a.lon}) AS punto_a,
         point({latitude: b.lat, longitude: b.lon}) AS punto_b

    WITH a, b, r,
         point.distance(punto_a, nuevo_punto) AS dist_a,
         point.distance(punto_b, nuevo_punto) AS dist_b

    CREATE (nuevo:Point {
        id: $local_id,
        lat: $lat,
        lon: $lon,
        name: $local_name,
        tipo: $local_tipo
    })

    CREATE (a)-[:STREET {
        name: r.name,
        length: dist_a,
        maxspeed: r.maxspeed,
        weight: r.weight * (dist_a / (dist_a + dist_b))
    }]->(nuevo)

    CREATE (nuevo)-[:STREET {
        name: r.name,
        length: dist_b,
        maxspeed: r.maxspeed,
        weight: r.weight * (dist_b / (dist_a + dist_b))
    }]->(b)

    DELETE r
    """

    with driver.session() as session:
        result = session.run(
            query,
            from_id=data.from_.id,
            to_id=data.to.id,
            lat=data.local.lat,
            lon=data.local.lon,
            local_id=data.local.id,
            local_name=data.local.name,
            local_tipo=data.local.tipo
        )
    return {"status": "ok", "mensaje": f"Se insertó el nodo {data.local.name} entre {data.from_.id} y {data.to.id}"}