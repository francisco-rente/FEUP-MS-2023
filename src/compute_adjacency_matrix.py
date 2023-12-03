import pickle
import numpy as np
import os
import pandas as pd
import networkx as nx
import geopandas as gpd

SECTIONS_GPKG = "../datasets/BGRI2021_1312.gpkg"
DEGREE_TO_METER = 111139

def read_sections_file():

    print(f'> Reading {SECTIONS_GPKG} file...')

    df = gpd.read_file(SECTIONS_GPKG)
    df = df.to_crs(epsg=4326) # WGS 84 coordinate system
  
    return df

def extract_centroids(df):
    df = df.to_crs(epsg=2263)
    df["centroid"] = df.centroid
    df = df.to_crs(epsg=4326)
    df["centroid"] = df["centroid"].to_crs(epsg=4326)
    
    centroids = []
    print(f'> Extracting centroids...')
    for _, r in df.iterrows():
        lat = r["centroid"].x
        lon = r["centroid"].y
        region_id = str(r["OBJECTID"])
        centroids.append((region_id, lat, lon))


    return centroids # 1659 centroids, 2752281 necessary checks

def distance_between_two_points(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) # * DEGREE_TO_METER

def insert_centroids_in_the_the_graph(G, centroids):
    for c in centroids:
        G.add_node(c[0], pos=(c[1], c[2]), type="Centroid")

        for n in G.nodes:
            if n != c[0] and not isCentroid(G.nodes[n]): # only stops 
                dist = distance_between_two_points(G.nodes[n]["pos"], (c[1], c[2]))
 # TODO: difference between weight and length here? 
                G.add_edge(c[0], n, weight=dist, length=dist, routes=[])
                G.add_edge(n, c[0], weight=dist, length=dist, routes=[])
    return G


def add_centroids_to_graph():
    with open('routes.gpickle', 'rb') as f:
        G = pickle.load(f)

    df = read_sections_file()
    centroids = extract_centroids(df)
    G = insert_centroids_in_the_the_graph(G, centroids)
    
    with open('routes_centroids.gpickle', 'wb') as f:
        pickle.dump(G, f)
    
    return G, centroids


def isCentroid(node):
    return 'type' in node and node['type'] == 'Centroid'

def extract_centroids_from_graph(G):
    return list(filter(lambda x: 'type' in G.nodes[x] and G.nodes[x]['type'] == 'Centroid', G.nodes()))


def compute_shortest_paths(G, centroids):

    if os.path.exists('paths.gpickle'):
        with open('paths.gpickle', 'rb') as f:
            return pickle.load(f)

    print(f'> Computing shortest paths between {len(centroids)} centroids...')
    paths = dict(nx.all_pairs_dijkstra_path_length(G, weight='weight')) # fastest I've found, use nx method only 
    print(f'> Shortest paths computed!')

    with open('paths.gpickle', 'wb') as f:
        pickle.dump(paths, f)

    return paths
    

def create_adjacency_matrix(paths, centroids):

    if os.path.exists('shortest_path.csv'):
        return pd.read_csv('shortest_path.csv')


    shortest_path_df = pd.DataFrame(columns=['from', 'to', 'distance'])

    matched_centroids = len(set(paths.keys()).intersection(set(centroids)))
    print(f'> Matched {matched_centroids} centroids out of {len(centroids)}')

    centroids_path = dict(filter(lambda p: p[0] in centroids, paths.items()))
    print(f'> Length of centroids_path: {len(centroids_path)}')

    distance_foo = lambda n, ps, c: ps[c] if c in ps \
                                            else 0 if n == c \
                                            else -1

    print(f'> Creating adjacency matrix...')
    shortest_path_arr = []
    for node, paths in centroids_path.items():
        for c in centroids:
            shortest_path_arr.append((node, c, distance_foo(node, paths, c)))
    
    shortest_path_df = pd.DataFrame(shortest_path_arr, columns=['from', 'to', 'distance'])
    return shortest_path_df


def metrics(matrix):
    # count number of -1
    print(f'> Number of -1: {matrix[matrix["distance"] == -1].shape[0]}, {matrix[matrix["distance"] == -1].shape[0]/matrix.shape[0]}')
    # get avg of all non -1 values
    print(f'> Avg distance: {matrix[matrix["distance"] != -1]["distance"].mean()}')


def main():

    if not os.path.exists('routes_centroids.gpickle'):
        G, centroids = add_centroids_to_graph()
    else:
        with open('routes_centroids.gpickle', 'rb') as f:
            G = pickle.load(f)
    
    centroids = extract_centroids_from_graph(G) 
    shortest_path_df = compute_shortest_paths(G, centroids)
    matrix = create_adjacency_matrix(shortest_path_df, centroids)
    metrics(matrix) 
    

    print("Saving shortest paths to csv file...")
    matrix.to_csv('shortest_path.csv', index=False)
    print("Shortest paths saved to csv file!")

if __name__ == '__main__':
    main()
