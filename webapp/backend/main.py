from fastapi import FastAPI, HTTPException, Depends, status, Form
from services.neo4j_connection import Neo4jConnection
from services.point_service import delete_map_point, insertar_nuevo_punto, list_map_points, obtener_tramo_cercano
from services.queries import obtener_puntos ,asegurar_proyeccion_grafo
from services.graph_services import crear_mapa_logistico, eliminar_mapa
import config
from algorithms import optimizacion_1,optimizacion_2 # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from models.schemes import Coordenadas, Intersection, PuntoEstablecimiento, InsercionRequest, MapaRequest
from auth.routes import auth_router, get_current_user
from auth.service import AuthService
from auth.models import UserResponse
import redis

conn = Neo4jConnection(config.URI, config.USER, config.PASSWORD)
# Conexión a Redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
app = FastAPI()

# Incluir rutas de autenticación
app.include_router(auth_router)

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Solo frontend
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "healthy", "service": "logistics-api"}

@app.post("/Mapa")
def crear_mapa(data: MapaRequest, current_user: UserResponse = Depends(get_current_user)):
    """Crear mapa - requiere autenticación"""
    return crear_mapa_logistico(data,conn)

@app.delete("/Mapa")
def borrar_mapa(current_user: UserResponse = Depends(get_current_user)):
    """Borrar mapa - requiere autenticación"""
    eliminar_mapa(conn)
    return {"Borrado": "Exitoso"}

@app.get("/puntos/mapa")
def get_puntos_mapa():
    return list_map_points(conn)

@app.delete("/punto/{id}")
def delete_punto(id: str, current_user: UserResponse = Depends(get_current_user)):
    """Eliminar punto - requiere autenticación"""
    return delete_map_point(id,conn)

@app.post("/ubicacion/tramo-cercano")
def get_tramo_cercano(coord: Coordenadas):
    return obtener_tramo_cercano(coord,conn)

@app.post("/ubicacion/insertar-local")
def insertar_local(data: InsercionRequest, current_user: UserResponse = Depends(get_current_user)):
    """Insertar local - requiere autenticación"""
    return insertar_nuevo_punto(data,conn)

@app.get("/calcularRuta")
def calcular_ruta_optima():
    asegurar_proyeccion_grafo(conn.driver)
    puntos_ids = obtener_puntos(conn.driver)
    #ordenar centro de distrubcion.
    result = optimizacion_1.ejecutarOptimizacion(conn.driver,puntos_ids)
    return result

@app.get("/Optimizacion2")
def correr_optimizacion2():
    result = optimizacion_2.ejecutarOptimizacion(conn.driver)
    return result

@app.get("/redis-test")
def test_redis():
    try:
        # Guardar un valor
        redis_client.set("test_key", "¡Redis funciona!")
        # Leer el valor
        value = redis_client.get("test_key")
        return {"redis_status": "conectado", "test_value": value}
    except Exception as e:
        return {"redis_status": "error", "message": str(e)}

@app.get("/PRUEBADOCKER")
def pruebadocker():
    return {"prueba": "docker"}