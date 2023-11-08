import partridge as ptg
import networkx as nx
import pickle

# Load GTFS data into a feed
gtfs_directory = '../datasets/gtfs-stcp'
feed = ptg.load_feed(gtfs_directory)
routes = feed.routes['route_id']
stops = feed.stops

# Create a spatial layout based on stop coordinates
pos = {stop_id: (lon, lat) for stop_id, lat, lon in zip(stops['stop_id'], stops['stop_lat'], stops['stop_lon'])}

# Create a directed graph to represent the trips
G = nx.DiGraph()

for _, route in routes.items():
    print(f'> Working on route: {route}')

    # Filter trips for direction_id == 0 and get the first trip
    first_trip_direction_0 = feed.trips[(feed.trips['route_id'] == route) & (feed.trips['direction_id'] == 0)].iloc[0]
    stop_times_direction_0 = feed.stop_times[feed.stop_times['trip_id'] == first_trip_direction_0['trip_id']]
    stop_sequence = stop_times_direction_0['stop_sequence'].values
    for i in range(len(stop_sequence) - 1):
        from_stop = stop_times_direction_0[stop_times_direction_0['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
        to_stop = stop_times_direction_0[stop_times_direction_0['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
        if from_stop not in G.nodes:
            G.add_node(from_stop, pos=pos[from_stop])
        if to_stop not in G.nodes:
            G.add_node(to_stop, pos=pos[to_stop])
        G.add_edge(from_stop, to_stop)

    # Filter trips for direction_id == 1 and get the first trip
    try:
        first_trip_direction_1 = feed.trips[(feed.trips['route_id'] == route) & (feed.trips['direction_id'] == 1)].iloc[0]
        stop_times_direction_1 = feed.stop_times[feed.stop_times['trip_id'] == first_trip_direction_1['trip_id']]
        stop_sequence = stop_times_direction_1['stop_sequence'].values
        for i in range(len(stop_sequence) - 1):
            from_stop = stop_times_direction_1[stop_times_direction_1['stop_sequence'] == stop_sequence[i]].iloc[0]['stop_id']
            to_stop = stop_times_direction_1[stop_times_direction_1['stop_sequence'] == stop_sequence[i + 1]].iloc[0]['stop_id']
            if from_stop not in G.nodes:
                G.add_node(from_stop, pos=pos[from_stop])
            if to_stop not in G.nodes:
                G.add_node(to_stop, pos=pos[to_stop])
            G.add_edge(from_stop, to_stop)
    except:
        continue

# Save graph object to file
with open('routes.gpickle', 'wb') as f:
    pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)