import networkx as nx
import utilities as util

def build_graph():
    # Load all component files from expansions directory
    components = {}
    component_files = [ 'components_core.json',
                        'components_accessories.json',
                        'components_propulsion.json',
                        'components_sensors.json',
                        'components_spraying.json' ]
    
    # Load all component files
    for filename in component_files:
        data = util.load_json_file(f'expansions/{filename}')
        for key, value in data.items():
            # Handle references to other files
            if isinstance(value, dict) and 'file' in value:
                ref_data = util.load_json_file(f"expansions/{value['file']}")
                components[key] = ref_data[value['id']]
            else:
                components[key] = value

    # Load connections from expansions directory
    connections = util.load_json_file('expansions/connections.json')

    # Create undirected graph
    G = nx.Graph()
    
    # Add nodes
    for component_id, component_data in components.items():
        G.add_node(component_id, **component_data)

    # Add edges - connections is now a list of pairs
    for connection in connections:
        G.add_edge(connection[0], connection[1])

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
    propulsion_components = util.load_json_file('expansions/components_propulsion.json')
    for component_id, data in components.items():
        if component_id in propulsion_components:
            path = get_path(G, 'avionics', component_id)
            if path:
                paths['avionics_to_propulsion'][component_id] = path

    # Paths from avionics to accessories
    paths['avionics_to_accessories'] = {}
    accessories_components = util.load_json_file('expansions/components_accessories.json')
    for component_id, data in components.items():
        if component_id in accessories_components:
            path = get_path(G, 'avionics', component_id)
            if path:
                paths['avionics_to_accessories'][component_id] = path

    # Paths from avionics to sensors (except antennas)
    paths['avionics_to_sensors'] = {}
    sensors_data = util.load_json_file('expansions/components_sensors.json')
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
    spraying_components = util.load_json_file('expansions/components_spraying.json')
    for component_id in spraying_components:
        path = get_path(G, 'spray_board', component_id, avoid_edges)
        if path:
            paths['spray_board_to_spraying'][component_id] = path

    # Save paths to file in expansions directory
    util.save_json_file('expansions/paths.json', paths)

if __name__ == '__main__':
    main()
