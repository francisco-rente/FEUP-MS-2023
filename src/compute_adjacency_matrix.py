import pickle
import numpy as np
import os
import pandas as pd
import networkx as nx
from concurrent.futures import ThreadPoolExecutor


def isCentroid(node):
    return node['type'] == 'centroid'


def extract_centroids_from_graph(G):
    return list(filter(lambda x: G.nodes[x]['type'] == 'centroid', G.nodes()))


def shortest_path(G, c1, c2):
    d = (c1, c2, nx.dijkstra_path_length(G, c1, c2, weight='weight')) if c1 != c2 else [c1, c2, 0]
    print(f'> Distance: {c1} -> {c2} = {d}')
    return d

def create_adjacency_matrix(G, centroids):

    if os.path.exists('shortest_path.csv'):
        return pd.read_csv('shortest_path.csv')

    shortest_path_df = pd.DataFrame(columns=['from', 'to', 'distance'])
    
    print(f'> Creating adjacency matrix...')
    shortest_path_arr = []
    with ThreadPoolExecutor() as executor:
        futures = []
        for c1 in centroids:
            for c2 in centroids:
                futures.append(executor.submit(shortest_path, G, c1, c2))
        print(f'> Waiting for results...')
        for future in futures:
            if future.result() is not None:
                shortest_path_arr.append(future.result())

    shortest_path_df = pd.DataFrame(shortest_path_arr, columns=['from', 'to', 'distance'])
    return shortest_path_df
    
    
def main():
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
   
    with open('graph.gpickle', 'rb') as f:
        G = pickle.load(f)
    
    centroids = extract_centroids_from_graph(G) 
    matrix = create_adjacency_matrix(G, centroids)

    print("Saving shortest paths to csv file...")
    matrix.to_csv('shortest_path.csv', index=False)
    print("Shortest paths saved to csv file!")

if __name__ == '__main__':
    main()
