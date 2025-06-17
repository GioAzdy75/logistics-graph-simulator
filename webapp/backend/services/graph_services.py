
import os
import shutil
from models.schemes import MapaRequest
from map_graph import graph_to_csv, import_data
import config

def crear_mapa_logistico(data: MapaRequest,conn):
    location = data.location # "Plaza Independencia, Mendoza, Argentina"
    radius = data.radio #3000
    graph_to_csv.graph_from_address_to_csv(location, radius)
    shutil.copy("nodes.csv", os.path.join(config.NEO4J_IMPORT_DIR, "nodes.csv"))
    shutil.copy("edges.csv", os.path.join(config.NEO4J_IMPORT_DIR, "edges.csv"))
    import_data.importar_csv(conn, "nodes.csv", "edges.csv")
    return {"Creado": "Exitoso"}

def eliminar_mapa(conn):
    query = """MATCH (n) DETACH DELETE n"""
    with conn.driver.session() as session:
        result = session.run(query)
        return result.single()