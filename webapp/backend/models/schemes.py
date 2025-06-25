from pydantic import BaseModel


class MapaRequest(BaseModel):
    location: str
    radio: int
    class Config:
        json_schema_extra = {
            "example": {
                "location": "Plaza Independencia, Mendoza, Argentina",
                "radio": 5000
            }
        }

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

class LoginRequest(BaseModel):
    username: str
    password: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

class User(BaseModel):
    id: int | None = None
    username: str
    email: str


