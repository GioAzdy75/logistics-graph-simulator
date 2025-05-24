
LIBERAR_MEMORIA = """
  CALL gds.graph.drop('mapa-logistico', false);
"""

MAPA_MEMORIA = """
CALL gds.graph.project(
  'mapa-logistico',
  {
    Point: {
      properties: ['lat', 'lon'] 
    }
  },
  {
    STREET: {
      properties: ['length', 'weight']
    }
  }
);
"""


def obtener_puntos(driver):
    query = """
    MATCH (p:Point)
    WHERE p.tipo IN ['Local', 'CentroDeDistribucion']
    RETURN p.id AS id, p.name AS nombre, p.lat AS lat, p.lon AS lon, p.tipo AS tipo
    """
    with driver.session() as session:
        result = session.run(query)
        return [record.data() for record in result]



def asegurar_proyeccion_grafo(driver):
    """
    Verifica si el grafo 'mapa-logistico' existe.
    Si existe y se requiere regenerarlo (por nodos nuevos), lo elimina y lo vuelve a crear.
    """
    with driver.session() as session:
        # Verificamos si ya existe
        result = session.run("CALL gds.graph.exists('mapa-logistico') YIELD exists RETURN exists")
        exists = result.single()["exists"]

        if exists:
            #print("El grafo ya existe. Eliminando para reconstruir...")
            session.run("CALL gds.graph.drop('mapa-logistico', false)")

        #print("Creando grafo 'mapa-logistico'...")
        session.run("""
            CALL gds.graph.project(
                'mapa-logistico',
                {
                    Point: {
                        properties: ['lat', 'lon']
                    }
                },
                {
                    STREET: {
                        properties: ['length', 'weight']
                    }
                }
            )
        """)
