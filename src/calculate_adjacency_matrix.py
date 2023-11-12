import pickle
import numpy as np
import pandas as pd
import networkx as nx

STCP_SHAPE = "../datasets/gtfs-stcp/shapes.txt"

def append_distances_to_graph(G):
    stcp_shapes = pd.read_csv(STCP_SHAPE, sep=',')
    stcp_shapes = read_shapes_and_extract_polylines(stcp_shapes)
    print(stcp_shapes.head())
    
    # for all edges that connect two stops
        # get the route path line and figure out the two points that are closest to the stops
        # calculate the distance between those two points over all intermediate points
        # add the distance as an edge attribute

    for edge in G.edges():
        if 'Centroid' not in G.nodes[edge[0]]['type'] and 'Centroid' not in G.nodes[edge[1]]['type']:
            print('Computing distance between {} and {}'.format(edge[0], edge[1]))
            route_id = G.edges[edge]['routes'][0] # TODO: try all for maximum detail
            print('Route id: {}'.format(route_id))

            route_shape = stcp_shapes[stcp_shapes['shape_id'] == route_id]['shape_pt_sequence'].values[0]
            print('Node contents: {}'.format(G.nodes[edge[0]]))

            # flip coordinates x, y y, x
            source = G.nodes[edge[0]]['pos']
            source = np.array([source[1], source[0]])
            target = G.nodes[edge[1]]['pos']
            target = np.array([target[1], target[0]])
            
            print('Source: {}'.format(source))
            print('Target: {}'.format(target))
            print('Route shape: {}'.format(route_shape))

            closest_to_source = np.argmin(np.linalg.norm(route_shape - source, axis=1))
            closest_to_target = np.argmin(np.linalg.norm(route_shape - target, axis=1))

            print('Closest to source: {}'.format(closest_to_source))
            print('Closest to target: {}'.format(closest_to_target))

            # compute distance between source intermediate point and target intermediate point
            distance = 0
            for i in range(closest_to_source, closest_to_target):
                distance += np.linalg.norm(route_shape[i] - route_shape[i+1])
            
            

            print('Distance: {}'.format(distance))
            
            # ask for input 
            input('Press enter to continue...')
            
            ARBITRARY_DISTANCE = 0.0001
            G.edges[edge]['weight'] = distance * ARBITRARY_DISTANCE
       
    return G





# TODO: move to utils
def read_shapes_and_extract_polylines(df):
    print('Reading shapes and extracting polylines...')

    # for each shape_id, create a list of (lat, lon) tuples
    df_route = pd.DataFrame()
    for shape_id in df['shape_id'].unique():
        df_route = df_route._append({'shape_id': shape_id.split('_')[0], \
                'shape_pt_sequence': np.array(list(zip(\
                    df[df['shape_id'] == shape_id]['shape_pt_lat'], 
                    df[df['shape_id'] == shape_id]['shape_pt_lon'])))},
                ignore_index=True)
    
    return df_route




def compute_shortest_paths(G):
    shortest_path_df = pd.DataFrame()

#    sources = list(filter(lambda x: 'type' in G.nodes[x] and G.nodes[x]['type'] == 'Centroid', G.nodes()))
#    shortest_path_dict = nx.multi_source_dijkstra(G, sources, weight='weight')

    for source in G.nodes():
        if 'type' in G.nodes[source] and G.nodes[source]['type'] == 'Centroid':
            for target in G.nodes():
                if source == target:
                    continue
                if 'type' in G.nodes[target] and G.nodes[target]['type'] == 'Centroid':
                    try :
                        print('Computing shortest path between {} and {}'.format(source, target))
                        le = nx.shortest_path_length(G, source, target, weight='weight')
                        print('Shortest path length: {}'.format(le))
                        shortest_path_df = shortest_path_df._append(\
                                {'source': source, \
                                'target': target, \
                                'shortest_path': le},
                                ignore_index=True)
                    except nx.NetworkXNoPath:
                        print('No path between {} and {}'.format(source, target))
                        shortest_path_df = shortest_path_df._append(\
                                {'source': source, \
                                'target': target, \
                                'shortest_path': -1}, ignore_index=True)

    return shortest_path_df


def main():
    with open('routes_centroids.gpickle', 'rb') as f:
        G = pickle.load(f)
    
    G = append_distances_to_graph(G)
    shortest_path_df = compute_shortest_paths(G)
    print(shortest_path_df.head())


if __name__ == '__main__':
    main()
