import osmnx as ox
import pandas as pd

def clean_maxspeed(G):
    for edge in G.edges:
        maxspeed = 40
        if "maxspeed" in G.edges[edge]:
            maxspeed = G.edges[edge]["maxspeed"]
            if isinstance(maxspeed, list):
                speeds = [int(speed) for speed in maxspeed if str(speed).isdigit()]
                maxspeed = min(speeds) if speeds else 40
            elif isinstance(maxspeed, str):
                try:
                    maxspeed = int(maxspeed.split()[0])
                except:
                    maxspeed = 40
        G.edges[edge]["maxspeed"] = maxspeed
        G.edges[edge]["weight"] = G.edges[edge]["length"] / maxspeed
    return G

def export_graph(graph, file_prefix=""):
    graph = clean_maxspeed(graph)
    nodes, edges = ox.convert.graph_to_gdfs(graph)

    # NODOS
    nodes_csv = nodes.reset_index()[['osmid', 'y', 'x']]
    nodes_csv.columns = ['node_id:ID', 'lat:float', 'lon:float']
    nodes_csv['tipo:string'] = 'Interseccion'
    nodes_csv[':LABEL'] = 'Point'
    nodes_csv.to_csv(f'{file_prefix}nodes.csv', index=False)

    # ARISTAS
    edges_csv = edges.reset_index()[['u', 'v', 'name', 'length', 'maxspeed', 'weight']]
    edges_csv.columns = [':START_ID', ':END_ID', 'name:string', 'length:float', 'maxspeed:int', 'weight:float']
    edges_csv[':TYPE'] = 'STREET'
    edges_csv.to_csv(f'{file_prefix}edges.csv', index=False)

def graph_from_address_to_csv(place: str, radius: int):
    graph = ox.graph_from_address(place, dist=radius, network_type="drive")
    export_graph(graph)

def graph_from_place_to_csv(place: str):
    graph = ox.graph_from_place(place, network_type="drive")
    export_graph(graph)
