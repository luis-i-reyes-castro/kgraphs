import json
import networkx as nx
from pathlib import Path

def load_json_file(filename):
    with open(filename, 'r') as f:
        return json.load(f)

def build_graph():
    # Load all component files
    components = {}
    for filename in ['T40_components_core.json', 'T40_components_accessories.json', 
                    'T40_components_propulsion.json', 'T40_components_sensors.json',
                    'T40_components_spraying.json']:
        data = load_json_file(filename)
        for key, value in data.items():
            # Handle references to other files
            if isinstance(value, dict) and 'file' in value:
                ref_data = load_json_file(value['file'])
                components[key] = ref_data[value['id']]
            else:
                components[key] = value

    # Load connections
    connections = load_json_file('T40_connections.json')

    # Create undirected graph
    G = nx.Graph()
    
    # Add nodes
    for component_id, component_data in components.items():
        G.add_node(component_id, **component_data)

    # Add edges
    for connection in connections['T40_connections']:
        G.add_edge(connection['from'], connection['to'])

    return G, components

def get_path(G, start, end, avoid_edges=None):
    if avoid_edges:
        # Create a copy of the graph without the edges to avoid
        H = G.copy()
        H.remove_edges_from(avoid_edges)
        try:
            return nx.shortest_path(H, start, end)
        except nx.NetworkXNoPath:
            return None
    return nx.shortest_path(G, start, end)

def main():
    G, components = build_graph()
    paths = {}

    # Paths from avionics to propulsion components
    paths['avionics_to_propulsion'] = {}
    for component_id, data in components.items():
        if component_id in load_json_file('T40_components_propulsion.json'):
            path = get_path(G, 'avionics', component_id)
            if path:
                paths['avionics_to_propulsion'][component_id] = path

    # Paths from avionics to accessories
    paths['avionics_to_accessories'] = {}
    for component_id, data in components.items():
        if component_id in load_json_file('T40_components_accessories.json'):
            path = get_path(G, 'avionics', component_id)
            if path:
                paths['avionics_to_accessories'][component_id] = path

    # Paths from avionics to sensors (except antennas)
    paths['avionics_to_sensors'] = {}
    sensors_data = load_json_file('T40_components_sensors.json')
    for component_id, data in sensors_data.items():
        if data.get('type') != 'antenna':
            path = get_path(G, 'avionics', component_id)
            if path:
                paths['avionics_to_sensors'][component_id] = path

    # Paths from rf_board to antennas
    paths['rf_board_to_antennas'] = {}
    for component_id, data in sensors_data.items():
        if data.get('type') == 'antenna':
            path = get_path(G, 'rf_board', component_id)
            if path:
                paths['rf_board_to_antennas'][component_id] = path

    # Paths from spray_board to spraying components
    # Avoid signal_cable_r when going from cdb to pdb
    avoid_edges = [('signal_cable_r', 'cdb'), ('signal_cable_r', 'pdb')]
    paths['spray_board_to_spraying'] = {}
    spraying_components = load_json_file('T40_components_spraying.json')
    for component_id in spraying_components:
        path = get_path(G, 'spray_board', component_id, avoid_edges)
        if path:
            paths['spray_board_to_spraying'][component_id] = path

    # Save paths to file
    with open('T40_paths.json', 'w') as f:
        json.dump(paths, f, indent=2)

if __name__ == '__main__':
    main() 