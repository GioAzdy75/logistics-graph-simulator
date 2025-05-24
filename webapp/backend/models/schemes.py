from pydantic import BaseModel


class MapaRequest(BaseModel):
    location: str
    radio: int

class Coordenadas(BaseModel):
    lat: float
    lon: float

class Intersection(BaseModel):
    id: str
    lat: float
    lon: float
    distancia_m: float | None = None  # opcional, no lo usamos para el insert

class PuntoEstablecimiento(BaseModel):
    id: str
    name: str
    lat: float
    lon: float
    tipo: str

class InsercionRequest(BaseModel):
    from_: Intersection
    to: Intersection
    calle: str
    local: PuntoEstablecimiento