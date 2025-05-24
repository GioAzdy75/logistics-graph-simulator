from fastapi import FastAPI
from services.neo4j_connection import Neo4jConnection
from services.point_service import delete_map_point, insertar_nuevo_punto, list_map_points, obtener_tramo_cercano
from services.queries import obtener_puntos ,asegurar_proyeccion_grafo
from services.graph_services import crear_mapa_logistico
import config
from algorithms import optimizacion_1,optimizacion_2
from fastapi.middleware.cors import CORSMiddleware
from models.schemes import Coordenadas, Intersection, PuntoEstablecimiento, InsercionRequest, MapaRequest

conn = Neo4jConnection(config.URI, config.USER, config.PASSWORD)
app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/Mapa")
def crear_mapa(data: MapaRequest):
    return crear_mapa_logistico(data,conn)

@app.delete("/Mapa")
def borrar_mapa():
    pass

@app.get("/puntos/mapa")
def get_puntos_mapa():
    return list_map_points(conn)

@app.delete("/punto/{id}")
def delete_punto(id: str):
    return delete_map_point(id,conn)

@app.post("/ubicacion/tramo-cercano")
def get_tramo_cercano(coord: Coordenadas):
    return obtener_tramo_cercano(coord,conn)

@app.post("/ubicacion/insertar-local")
def insertar_local(data: InsercionRequest):
    return insertar_nuevo_punto(data,conn)

@app.get("/calcularRuta")
def calcular_ruta_optima():
    asegurar_proyeccion_grafo(conn.driver)
    puntos_ids = obtener_puntos(conn.driver)
    result = optimizacion_1.ejecutarOptimizacion(conn.driver,puntos_ids)
    return result

@app.get("/Optimizacion2")
def correr_optimizacion2():
    result = optimizacion_2.ejecutarOptimizacion(conn.driver)
    return result