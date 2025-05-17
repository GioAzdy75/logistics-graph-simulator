


MAPA_MEMORIA = """
CALL gds.graph.project(
  'mapa-logistico',
  'Intersection',
  {
    STREET: {
      properties: ['length']
    }
  }
);
"""

