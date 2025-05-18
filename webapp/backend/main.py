from fastapi import FastAPI
from pydantic import BaseModel
from neo4j_connection import Neo4jConnection
from queries import MAPA_MEMORIA
import os
import sys

import config
from algorithms import optimizacion_1,optimizacion_2

#
from fastapi.middleware.cors import CORSMiddleware




#
class PointMap(BaseModel):
    name: str
    corX: float
    corY: float
    tipo: str

puntosMapa = []
count = 0


#coneccion a base de atos
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

#Crear Mapa
@app.post("/Mapa")
def crear_mapa():
    pass

#
@app.get("/Mapa")
def cargar_mapa_memoria():
    conn.query(MAPA_MEMORIA)
    return 

@app.get("/Punto")
def obtener_punto():
    return puntosMapa

#endpoint creacion de puntos (locales / centro de distribucion)
@app.post("/Punto")
def nuevo_punto(point : PointMap):
    global count
    #Raise error local/centro
    if point.tipo == "local" or point.tipo == "centro":
        point.name = point.name + f"{count}"
        puntosMapa.append(point)
        count += 1
    else:
        pass
    return ""

#ejecuta la ruta
from fastapi.responses import JSONResponse

@app.get("/calcularRuta")
def calcular_ruta_optima():
    #llamar la funcion que trae las intersecciones mas cercanas dada dos puntos de coordenadas

    #Nodos de prueba
    #llamar a la funcion que ejecuta la ruta
    result = optimizacion_1.ejecutarOptimizacion(conn.driver)
    
    #print()
    
    return result


@app.get("/Optimizacion2")
def correr_optimizacion2():
    result = optimizacion_2.ejecutarOptimizacion(conn.driver)
    return JSONResponse(content=result)