import osmnx as ox

def clean_maxspeed(G):
    for edge in G.edges:
        maxspeed = 40
        if "maxspeed" in G.edges[edge]:
            maxspeed = G.edges[edge]["maxspeed"]
            if type(maxspeed) == list:
                speeds = [ int(speed) for speed in maxspeed ]
                maxspeed = min(speeds)
            elif type(maxspeed) == str:
                maxspeed = int(maxspeed)
        G.edges[edge]["maxspeed"] = maxspeed
        G.edges[edge]["weight"] = G.edges[edge]["length"] / maxspeed
    return G

def graph_from_address_to_csv(place: str, radius: int): # e.g. place = "Plaza Independencia, Mendoza, Argentina"
    graph = ox.graph_from_address(place, dist=radius, network_type="drive")
    graph = clean_maxspeed(graph)
    nodes, edges = ox.convert.graph_to_gdfs(graph)

    # Limpiar nodos
    nodes_csv = nodes.reset_index()[['osmid', 'y', 'x']]
    nodes_csv.columns = ['node_id:ID', 'lat:float', 'lon:float']
    nodes_csv[':LABEL'] = 'Intersection'
    nodes_csv.to_csv('nodes.csv', index=False)

    # Limpiar aristas
    edges_csv = edges.reset_index()[['u', 'v', 'name', 'length']]  # u=origen, v=destino
    edges_csv.columns = [':START_ID', ':END_ID', 'name:string', 'length:float']
    edges_csv[':TYPE'] = 'STREET'
    edges_csv.to_csv('edges.csv', index=False)

def graph_from_place_to_csv(place: str): # e.g. place = "Mendoza, Argentina"
    graph = ox.graph_from_place(place, network_type="drive")
    graph = clean_maxspeed(graph)
    nodes, edges = ox.convert.graph_to_gdfs(graph)

    # Limpiar nodos
    nodes_csv = nodes.reset_index()[['osmid', 'y', 'x']]
    nodes_csv.columns = ['node_id:ID', 'lat:float', 'lon:float']
    nodes_csv[':LABEL'] = 'Intersection'
    nodes_csv.to_csv('nodes.csv', index=False)

    # Limpiar aristas
    edges_csv = edges.reset_index()[['u', 'v', 'name', 'length', 'maxspeed', 'weight']]  # u=origen, v=destino
    edges_csv.columns = [':START_ID', ':END_ID', 'name:string', 'length:float', 'maxspeed:int', 'weight:float']
    edges_csv[':TYPE'] = 'STREET'
    edges_csv.to_csv('edges.csv', index=False)
