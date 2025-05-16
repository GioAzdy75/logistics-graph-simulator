from typing import Union
from fastapi import FastAPI
from pydantic import BaseModel

class PointMap(BaseModel):
    name: str
    corX: float
    corY: float
    tipo: str

puntosMapa = []

app = FastAPI()

@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.post("/nuevoPunto")
def nuevoPunto(point : PointMap):
    #Raise error local/centro
    if point.tipo == "local" or point.tipo == "centro":
        puntosMapa.append(point)
    else:
        pass
    return ""

@app.get("/calcularRuta")
def calcular_ruta_optima():
    #llamar la funcion que trae las intersecciones mas cercanas dada dos puntos de coordenadas
    
    #llamar a la funcion que ejecuta la ruta

    return "" #Ruta

