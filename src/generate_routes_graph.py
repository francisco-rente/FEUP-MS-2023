import partridge as ptg
import networkx as nx
import pickle
import math


DEGREE_TO_METER = 111139


def add_routes(graph, feed, weight_prop=0.05, shapes=False):
    routes = feed.routes['route_id']

    stops = feed.stops
    pos = {stop_id: (lon, lat) for stop_id, lat, lon in zip(stops['stop_id'], stops['stop_lat'], stops['stop_lon'])}

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

        for i in range(len(shapes_raw) - 1):
            from_shape = shapes_raw[shapes_raw['shape_pt_sequence'] == shapes_sequence[i]].iloc[0]
            to_shape = shapes_raw[shapes_raw['shape_pt_sequence'] == shapes_sequence[i + 1]].iloc[0]
            from_lon, from_lat = from_shape['shape_pt_lon'], from_shape['shape_pt_lat']
            to_lon, to_lat = to_shape['shape_pt_lon'], to_shape['shape_pt_lat']
            distance = math.sqrt(((from_lon - to_lon) * DEGREE_TO_METER) ** 2 + ((from_lat - to_lat) * DEGREE_TO_METER) ** 2)
            if i == 0:
                shapes.append((from_lon, from_lat, 0))
            shapes.append((to_lon, to_lat, distance))
        
    stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id]
    stop_sequence = stop_times['stop_sequence'].values
    
    for i in range(len(stop_sequence) - 1):
        from_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
        to_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
        from_lon, from_lat = pos[from_stop]
        to_lon, to_lat = pos[to_stop]

        if shape_id:
            if i == 0:
                from_shape_dist = [math.dist((shapes[i][0], shapes[i][1]), (from_lon, from_lat)) + math.dist((shapes[i+1][0], shapes[i+1][1]), (from_lon, from_lat)) - math.dist((shapes[i][0], shapes[i][1]), (shapes[i+1][0], shapes[i+1][1])) for i in range(len(shapes) - 1)]
                from_shape_index = from_shape_dist.index(min(from_shape_dist))
                if math.dist((shapes[from_shape_index][0], shapes[from_shape_index][1]), (from_lon, from_lat)) > math.dist((shapes[from_shape_index + 1][0], shapes[from_shape_index + 1][1]), (from_lon, from_lat)): from_shape_index = from_shape_index + 1

            to_shape_dist = [math.dist((shapes[i][0], shapes[i][1]), (to_lon, to_lat)) + math.dist((shapes[i+1][0], shapes[i+1][1]), (to_lon, to_lat)) - math.dist((shapes[i][0], shapes[i][1]), (shapes[i+1][0], shapes[i+1][1])) for i in range(len(shapes[from_shape_index + 1]) - 1)]
            to_shape_index = to_shape_dist.index(min(to_shape_dist)) + from_shape_index + 1
            if math.dist((shapes[to_shape_index][0], shapes[to_shape_index][1]), (to_lon, to_lat)) > math.dist((shapes[to_shape_index + 1][0], shapes[to_shape_index + 1][1]), (to_lon, to_lat)): to_shape_index = to_shape_index + 1

            distance = sum([shapes[i][2] for i in range(from_shape_index + 1, to_shape_index + 1)]) + math.dist((shapes[from_shape_index][0], shapes[from_shape_index][1]), (from_lon, from_lat)) + math.dist((shapes[to_shape_index][0], shapes[to_shape_index][1]), (to_lon, to_lat))

            from_shape_index = to_shape_index
        else:
            distance = math.sqrt(((from_lon - to_lon) * DEGREE_TO_METER) ** 2 + ((from_lat - to_lat) * DEGREE_TO_METER) ** 2)
        
        if from_stop not in graph.nodes:
            graph.add_node(from_stop, pos=(from_lon, from_lat))
        if to_stop not in graph.nodes:
            graph.add_node(to_stop, pos=(to_lon, to_lat))
        edge_routes = graph.get_edge_data(from_stop, to_stop, {}).get('routes', [])
        edge_routes.append(route)
        graph.add_edge(from_stop, to_stop, weight=distance*weight_prop, length=distance, debug_length=math.sqrt(((from_lon - to_lon) * DEGREE_TO_METER) ** 2 + ((from_lat - to_lat) * DEGREE_TO_METER) ** 2), routes=edge_routes)


def main():
    # Load GTFS data into a feed
    stcp_feed = ptg.load_feed('../datasets/gtfs-stcp')
    mdp_feed = ptg.load_feed('../datasets/gtfs-mdp')

    # Create a directed graph to represent the trips
    G = nx.DiGraph()

    # Generate graph
    print('################# STCP #################')
    add_routes(G, stcp_feed, shapes=True)
    print('################# MDP #################')
    add_routes(G, mdp_feed, weight_prop=0.01)

    # Save graph object to file 
    with open('routes.gpickle', 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)

    with open('debug.log', 'w') as f:
        for from_stop, to_stop, data in G.edges(data=True):
            f.write(f'{from_stop}-{to_stop}, {data}\n')


if __name__ == '__main__':
    main()
