from fastapi import FastAPI, HTTPException, Depends, status, Form
from services.neo4j_connection import Neo4jConnection
from services.point_service import delete_map_point, insertar_nuevo_punto, list_map_points, obtener_tramo_cercano
from services.queries import obtener_puntos ,asegurar_proyeccion_grafo
from services.graph_services import crear_mapa_logistico, eliminar_mapa
import config
from algorithms import optimizacion_1,optimizacion_2 # type: ignore
from fastapi.middleware.cors import CORSMiddleware
from models.schemes import Coordenadas, Intersection, PuntoEstablecimiento, InsercionRequest, MapaRequest, LoginRequest, LoginResponse
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer
import redis

conn = Neo4jConnection(config.URI, config.USER, config.PASSWORD)
# Conexión a Redis
redis_client = redis.Redis(host='redis', port=6379, db=0, decode_responses=True)
app = FastAPI()

#CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Usuario de ejemplo (en producción, usar base de datos y contraseñas hasheadas)
FAKE_USER = {
    "username": "admin",
    "password": "admin123",
    "email": "admin@example.com"
}

SECRET_KEY = "supersecretkey"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

def verify_token(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") # type: ignore
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido")
        return username
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token inválido o expirado")

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/Mapa")
def crear_mapa(data: MapaRequest):
    return crear_mapa_logistico(data,conn)

@app.delete("/Mapa")
def borrar_mapa():
    eliminar_mapa(conn)
    return {"Borrado": "Exitoso"}

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
    #ordenar centro de distrubcion.
    result = optimizacion_1.ejecutarOptimizacion(conn.driver,puntos_ids)
    return result

@app.get("/Optimizacion2")
def correr_optimizacion2():
    result = optimizacion_2.ejecutarOptimizacion(conn.driver)
    return result


@app.post("/login", response_model=LoginResponse)
def login(username: str = Form(...), password: str = Form(...)):
    if username != FAKE_USER["username"] or password != FAKE_USER["password"]:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    expire = datetime.now() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"sub": username, "exp": int(expire.timestamp())}  # exp como timestamp
    access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return LoginResponse(access_token=access_token)

@app.get("/protegido")
def ruta_protegida(username: str = Depends(verify_token)):
    return {"mensaje": f"Acceso concedido a {username}"}

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