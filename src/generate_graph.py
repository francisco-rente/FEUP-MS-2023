import argparse
import partridge as ptg
import networkx as nx
import pickle
import math
import geopandas as gpd


DEGREE_TO_METER = 111139
MAX_WALKING_DISTANCE = 2000     # NOTE: In m


def add_routes(graph, feed, weight_prop=0.05, shapes=False):
    routes = feed.routes['route_id']

    stops = feed.stops
    pos = {stop_id: (lat, lon) for stop_id, lat, lon in zip(stops['stop_id'], stops['stop_lat'], stops['stop_lon'])}

    for _, route in routes.items():
        print(f'> Working on route: {route}')
        add_route(graph, feed, pos, route, weight_prop, shapes)


def add_route(graph, feed, pos, route, weight_prop, shapes):
    for dir in [0, 1]:
        try:
            trip = feed.trips[(feed.trips['route_id'] == route) & (feed.trips['direction_id'] == dir)].iloc[0]
        except:
            print(f'> WARNING: No direction {dir} for route {route}')
            continue
        trip_id = trip['trip_id']
        if shapes:
            add_trip(graph, feed, pos, route, weight_prop, trip_id, trip['shape_id'])
        else:
            add_trip(graph, feed, pos, route, weight_prop, trip_id)
    

def add_trip(graph, feed, pos, route, weight_prop, trip_id, shape_id=None):

    if shape_id:
        shapes_raw = feed.shapes[feed.shapes['shape_id'] == shape_id]
        shapes_sequence = shapes_raw['shape_pt_sequence'].values
        shapes = []

        for i in range(len(shapes_raw) - 1):    # TODO: Optimize by saving to_shape for next iteration
            from_shape = shapes_raw[shapes_raw['shape_pt_sequence'] == shapes_sequence[i]].iloc[0]
            to_shape = shapes_raw[shapes_raw['shape_pt_sequence'] == shapes_sequence[i + 1]].iloc[0]
            from_lat, from_lon = from_shape['shape_pt_lat'], from_shape['shape_pt_lon']
            to_lat, to_lon = to_shape['shape_pt_lat'], to_shape['shape_pt_lon']
            distance = calculate_distance_degree((from_lat, from_lon), (to_lat, to_lon))
            if i == 0:
                shapes.append((from_lat, from_lon, 0))
            shapes.append((to_lat, to_lon, distance))
            
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id]
    stop_sequence = stop_times['stop_sequence'].values
    
    for i in range(len(stop_sequence) - 1):
        from_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
        to_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
        from_lat, from_lon = pos[from_stop]
        to_lat, to_lon = pos[to_stop]

        if shape_id:
            if i == 0:
                from_shape_dist = [math.dist((shapes[i][0], shapes[i][1]), (from_lat, from_lon)) for i in range(len(shapes))]
                from_shape_index = from_shape_dist.index(min(from_shape_dist))

            to_shape_dist = [math.dist((shapes[i][0], shapes[i][1]), (to_lat, to_lon)) for i in range(from_shape_index, len(shapes))]
            to_shape_index = to_shape_dist.index(min(to_shape_dist)) + from_shape_index

            distance = sum([shapes[i][2] for i in range(from_shape_index + 1, to_shape_index + 1)]) + calculate_distance_degree((shapes[from_shape_index][0], shapes[from_shape_index][1]), (from_lat, from_lon)) + calculate_distance_degree((shapes[to_shape_index][0], shapes[to_shape_index][1]), (to_lat, to_lon))

            from_shape_index = to_shape_index
        else:
            distance = calculate_distance_degree((from_lat, from_lon), (to_lat, to_lon))
        
        if from_stop not in graph.nodes:
            graph.add_node(from_stop, pos=(from_lat, from_lon), type='stop')

        if to_stop not in graph.nodes:
            graph.add_node(to_stop, pos=(to_lat, to_lon), type='stop')

        # NOTE: There are pairs of stops shared through multiple routes
        edge_routes = graph.get_edge_data(from_stop, to_stop, {}).get('routes', [])
        edge_routes.append(route)

        # NOTE: As shapes from different shared pairs of stops can varie, their distance varies to, we accept the min distance
        if graph.has_edge(from_stop, to_stop):
            graph_distance = graph.get_edge_data(from_stop, to_stop)['distance']
            distance = min(graph_distance, distance)

        # NOTE: For DEBUG purposes you can add debug_distance=calculate_distance_degree((from_lon, from_lat), (to_lon, to_lat)) to the edge attributes
        graph.add_edge(from_stop, to_stop, weight=distance*weight_prop, distance=distance, routes=edge_routes)


def load_centroids(path):
    df = gpd.read_file(path)
    df['centroid'] = df.centroid.to_crs(epsg=4326)
    
    centroids = []
    for _, r in df.iterrows():
        lat, lon = r['centroid'].y, r['centroid'].x
        region_id = str(r['OBJECTID'])
        centroids.append((region_id, lat, lon))

    return centroids


def add_centroids(G, centroids):    
    for c in centroids:
        print(f'> Adding section: {c[0]}')
        G.add_node(c[0], pos=(c[1], c[2]), type='centroid')


def connect_nodes_without_edge(G, max_walking_distance=1e9):
    for x in G.nodes:
        for y in G.nodes:
            if x != y and not G.has_edge(x, y):
                distance = calculate_distance_degree(G.nodes[x]['pos'], G.nodes[y]['pos'])
                if distance < max_walking_distance:
                    G.add_edge(x, y, weight=distance, distance=distance)


def calculate_distance_degree(from_pos, to_pos):
    return math.sqrt(sum(((px - qx) * DEGREE_TO_METER) ** 2 for px, qx in zip(from_pos, to_pos)))


def main():
    parser = argparse.ArgumentParser(description='Generates a graph with GTFS stops/routes and GPKG centroids, connects those in walking distance.')
    parser.add_argument('--gtfs', type=str, nargs='+', help='PATH to one or more GTFS', required=True)
    parser.add_argument('--wf', type=float, nargs='+', help='Weight factors corresponding to GTFS paths', required=True)
    parser.add_argument('--shapes', type=bool, nargs='+', help='Use shapes from GTFS paths for more accurate distances', required=True)
    parser.add_argument('--gpkg', type=str, nargs='+', help='PATH to one or more GPKG', required=True)
    parser.add_argument('--out', type=str, help='PATH to output file', required=True)
    args = parser.parse_args()

    gtfs_paths = args.gtfs
    weight_factors = args.wf
    use_shapes = args.shapes
    gpkg_paths = args.gpkg
    outfile_path = args.out

    if len(gtfs_paths) != len(weight_factors) != len(use_shapes):
        parser.error("The number of GTFS paths, weight factors and shapes must be the same.")

    # Create a directed graph to represent the trips
    G = nx.DiGraph()

    for i, gtfs_path in enumerate(gtfs_paths):
        # Load GTFS data into a feed
        print(f'> Reading GTFS: {gtfs_path}')
        feed = ptg.load_feed(gtfs_path)

        # Generate graph
        print(f'> Inserting routes from {gtfs_path}')
        add_routes(G, feed, weight_prop=weight_factors[i], shapes=use_shapes[i])

    for gpkg_path in gpkg_paths:
        # Load GPKG
        print(f'> Reading GPKG: {gpkg_path}')
        sections = load_centroids(gpkg_path)

        # Generate graph
        print(f'> Inserting centroids from {gpkg_path}')
        add_centroids(G, sections)

    print(f'> Connecting all nodes without connecting edges with weight=distance (max. walking distance is {MAX_WALKING_DISTANCE}m)')
    connect_nodes_without_edge(G, max_walking_distance=MAX_WALKING_DISTANCE)

    # Check connectivity
    if nx.is_strongly_connected(G):
        print('> The graph is strongly connected')
    else:
        print("> WARNING: The graph isn't strongly connected!")

    # Save graph object to file 
    with open(outfile_path, 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)

    # with open('debug.log', 'w') as f:
    #     for from_stop, to_stop, data in G.edges(data=True):
    #         f.write(f'{from_stop}-{to_stop}, {data}\n')


if __name__ == '__main__':
    main()
