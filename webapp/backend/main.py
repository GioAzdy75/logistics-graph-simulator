from fastapi import FastAPI
from pydantic import BaseModel
from neo4j_connection import Neo4jConnection
from queries import MAPA_MEMORIA ,obtener_puntos ,asegurar_proyeccion_grafo
import os
import sys
from fastapi import APIRouter, HTTPException
import config
from algorithms import optimizacion_1,optimizacion_2
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from schemes import Coordenadas,Intersection,PuntoEstablecimiento,InsercionRequest
from map_graph import graph_to_csv, import_data

#coneccion a base de datos
conn = Neo4jConnection(config.URI, config.USER, config.PASSWORD)

#inicializacion de base de datos
app = FastAPI()

#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # durante desarrollo, podés usar "*" o limitarlo a ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/Mapa")
def crear_mapa():
    location = "Plaza Independencia, Mendoza, Argentina"
    radius = 3000
    """
    try:
        graph_to_csv.graph_from_address_to_csv(location, radius)
    except:
        graph_to_csv.graph_from_place_to_csv(location)
    """
    import_data.importar_csv(conn, "nodes.csv", "edges.csv")
    return {"Creado": "Exitoso"}

@app.get("/Mapa")
def cargar_mapa_memoria():
    conn.query(MAPA_MEMORIA)
    return 

@app.get("/puntos/mapa")
def obtener_puntos_mapa():
    query = """
    MATCH (p:Point)
    WHERE p.tipo IN ['Local', 'CentroDeDistribucion']
    RETURN p.id AS id, p.name AS nombre, p.lat AS lat, p.lon AS lon, p.tipo AS tipo
    """
    with conn.driver.session() as session:
        result = session.run(query)
        puntos = [record.data() for record in result]
    return JSONResponse(content=puntos)


@app.delete("/punto/{id}")
def eliminar_punto(id: str):
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


@app.post("/ubicacion/tramo-cercano")
def obtener_tramo_cercano(coord: Coordenadas):
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


@app.post("/ubicacion/insertar-local")
def insertar_local(data: InsercionRequest):
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

@app.get("/calcularRuta")
def calcular_ruta_optima():
    asegurar_proyeccion_grafo(conn.driver)
    #llamar la funcion que trae las intersecciones mas cercanas dada dos puntos de coordenadas

    #Nodos de prueba
    puntos_ids = obtener_puntos(conn.driver)
    #llamar a la funcion que ejecuta la ruta
    result = optimizacion_1.ejecutarOptimizacion(conn.driver,puntos_ids)
    
    #print()
    
    return result

@app.get("/Optimizacion2")
def correr_optimizacion2():
    result = optimizacion_2.ejecutarOptimizacion(conn.driver)
    return JSONResponse(content=result)