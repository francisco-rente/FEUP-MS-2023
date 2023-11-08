import partridge as ptg
import networkx as nx
import pickle
import math


DEGREE_TO_METER = 111139


def add_routes(graph, feed, weight_prop=0.05):
    routes = feed.routes['route_id']

    stops = feed.stops
    pos = {stop_id: (lon, lat) for stop_id, lat, lon in zip(stops['stop_id'], stops['stop_lat'], stops['stop_lon'])}

    for _, route in routes.items():
        print(f'> Working on route: {route}')
        add_route(graph, feed, pos, route, weight_prop)


def add_route(graph, feed, pos, route, weight_prop):
    for dir in [0, 1]:
        try:
            trip_id = feed.trips[(feed.trips['route_id'] == route) & (feed.trips['direction_id'] == dir)].iloc[0]['trip_id']
        except:
            print(f'> WARNING: No direction {dir} for route {route}')
            continue
        stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id]
        stop_sequence = stop_times['stop_sequence'].values
        add_trip(graph, pos, route, stop_times, stop_sequence, weight_prop)


def add_trip(graph, pos, route, stop_times, stop_sequence, weight_prop):
    for i in range(len(stop_sequence) - 1):
        from_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
        to_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
        from_pos, to_pos = pos[from_stop], pos[to_stop]
        distance = math.sqrt(((from_pos[0] - to_pos[0]) * DEGREE_TO_METER) ** 2 + ((from_pos[1] - to_pos[1]) * DEGREE_TO_METER) ** 2)
        if from_stop not in graph.nodes:
            graph.add_node(from_stop, pos=from_pos)
        if to_stop not in graph.nodes:
            graph.add_node(to_stop, pos=to_pos)
        edge_routes = graph.get_edge_data(from_stop, to_stop, {}).get('routes', [])
        edge_routes.append(route)
        graph.add_edge(from_stop, to_stop, weight=distance*weight_prop, length=distance, routes=edge_routes)


def main():
    # Load GTFS data into a feed
    stcp_feed = ptg.load_feed('../datasets/gtfs-stcp')
    mdp_feed = ptg.load_feed('../datasets/gtfs-mdp')

    # Create a directed graph to represent the trips
    G = nx.DiGraph()

    # Generate graph
    print('################# STCP #################')
    add_routes(G, stcp_feed)
    print('################# MDP #################')
    add_routes(G, mdp_feed, 0.01)

    # Save graph object to file 
    with open('routes.gpickle', 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)

    with open('debug.log', 'w') as f:
        for from_stop, to_stop, data in G.edges(data=True):
            f.write(f'{from_stop}-{to_stop}, {data}\n')


if __name__ == '__main__':
    main()
