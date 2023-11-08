import partridge as ptg
import networkx as nx
import pickle


def add_routes(graph, feed):
    routes = feed.routes['route_id']

    # Create a spatial layout based on stop coordinates
    stops = feed.stops
    pos = {stop_id: (lon, lat) for stop_id, lat, lon in zip(stops['stop_id'], stops['stop_lat'], stops['stop_lon'])}

    for _, route in routes.items():
        print(f'> Working on route: {route}')
        add_route(graph, feed, pos, route)


def add_route(graph, feed, pos, route):
    for dir in [0, 1]:
        try:
            trip_id = feed.trips[(feed.trips['route_id'] == route) & (feed.trips['direction_id'] == dir)].iloc[0]['trip_id']
        except:
            print(f'> WARNING: No direction {dir} for route {route}')
            continue
        stop_times = feed.stop_times[feed.stop_times['trip_id'] == trip_id]
        stop_sequence = stop_times['stop_sequence'].values
        add_trip(graph, pos, route, stop_times, stop_sequence)


def add_trip(graph, pos, route, stop_times, stop_sequence):
    for i in range(len(stop_sequence) - 1):
        from_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
        to_stop = stop_times[stop_times['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
        if from_stop not in graph.nodes:
            graph.add_node(from_stop, pos=pos[from_stop])
        if to_stop not in graph.nodes:
            graph.add_node(to_stop, pos=pos[to_stop])
        graph.add_edge(from_stop, to_stop)


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
    add_routes(G, mdp_feed)

    # Save graph object to file
    with open('routes.gpickle', 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
