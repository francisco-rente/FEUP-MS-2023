import pickle
import numpy as np
import os
import pandas as pd
import networkx as nx
import geopandas as gpd
import math

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
        region_id = r["OBJECTID"]
        centroids.append((region_id, lat, lon))
    # 1659 centroids, 2752281 necessary checks
    print(f'> {len(centroids)} centroids extracted, no of necessary checks: {len(centroids)**2}')

    return centroids

def distance_between_two_points(p1, p2):
    return np.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2) # * DEGREE_TO_METER


def insert_centroids_in_the_the_graph(G, centroids):
    for c in centroids:
        G.add_node(c[0], pos=(c[1], c[2]), type="Centroid")

        for n in G.nodes:
            dist = distance_between_two_points(G.nodes[n]["pos"], (c[1], c[2]))
            G.add_edge(c[0], n, weight=dist, length=0, routes=[])
         
    return G


def add_centroids_to_graph():
    with open('routes.gpickle', 'rb') as f:
        G = pickle.load(f)

    df = read_sections_file()
    centroids = extract_centroids(df)
    G = insert_centroids_in_the_the_graph(G, centroids)
    
    with open('routes_centroids.gpickle', 'wb') as f:
        pickle.dump(G, f)
    
    return G


def isCentroid(node):
    return 'type' in node and node['type'] == 'Centroid'


def compute_shortest_paths(G):
    shortest_path_df = pd.DataFrame()

#   sources = list(filter(lambda x: 'type' in G.nodes[x] and G.nodes[x]['type'] == 'Centroid', G.nodes()))
#   shortest_path_dict = nx.multi_source_dijkstra(G, sources, weight='weight')

    for source in G.nodes():
        if isCentroid(G.nodes[source]):
            # print content of the node
            print('Source: {}'.format(source))
            for target in G.nodes():
                if source != target and  isCentroid(G.nodes[target]):
                    try :
#                        print('Computing shortest path between {} and {}'.format(source, target))
                        le = nx.shortest_path_length(G, source, target, weight='weight')
#                        print(f'Shortest path length: {le}')
                        shortest_path_df = shortest_path_df._append(\
                                {'source': source, \
                                'target': target, \
                                'shortest_path': le},
                                ignore_index=True)
                    except nx.NetworkXNoPath:
                        # print('No path between {} and {}'.format(source, target))
                        shortest_path_df = shortest_path_df._append(\
                                {'source': source, \
                                'target': target, \
                                'shortest_path': -1}, ignore_index=True)

    return shortest_path_df


def main():

    if not os.path.exists('routes_centroids.gpickle'):
        G =  add_centroids_to_graph()
    else:
        with open('routes_centroids.gpickle', 'rb') as f:
            G = pickle.load(f)
    
    shortest_path_df = compute_shortest_paths(G)
    
    print("Saving shortest paths to csv file...")
    shortest_path_df.to_csv('shortest_path.csv', index=False)


if __name__ == '__main__':
    main()
