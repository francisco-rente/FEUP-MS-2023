import pickle
import os
import pandas as pd
import networkx as nx
from concurrent.futures import ThreadPoolExecutor
import math
from utils import timed


def isCentroid(node):
    return node['type'] == 'centroid'


def extract_centroids_from_graph(G):
    return list(filter(lambda x: G.nodes[x]['type'] == 'centroid', G.nodes()))


@timed
def shortest_dijkstra_path(G, c1, c2):
    p = nx.dijkstra_path(G, c1, c2)
    d = sum([G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1)])
    return (c1, c2, '-'.join(p), d)


@timed
def shortest_astar_path(G, c1, c2):
    p = nx.astar_path(G, c1, c2, heuristic=lambda x, y: math.dist(G.nodes[x]['pos'], G.nodes[y]['pos'])) 
    d = sum([G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1)])
    return (c1, c2, '-'.join(p), d)


def create_adjacency_matrix(G, centroids, debug=False):
    shortest_path_df = pd.DataFrame(columns=['from', 'to', 'path', 'distance'])
    
    print(f'> Creating adjacency matrix...')
    shortest_path_arr = []

    if debug:
        count = 0
    
    with ThreadPoolExecutor() as executor:
        futures = []
        for c1 in centroids:
            for c2 in centroids:
                futures.append(executor.submit(shortest_astar_path, G, c1, c2))
                if debug:
                    count += 1
                    if count > 4:
                        break
            if debug:
                break
        print(f'> Waiting for results...')
        for future in futures:
            if future.result() is not None:
                shortest_path_arr.append(future.result())

    shortest_path_df = pd.DataFrame(shortest_path_arr, columns=['from', 'to', 'path', 'distance'])
    return shortest_path_df
    
    
def main():
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
   
    with open('graph.gpickle', 'rb') as f:
        G = pickle.load(f)
    
    centroids = extract_centroids_from_graph(G) 
    matrix = create_adjacency_matrix(G, centroids, debug=True)

    print("> Saving shortest paths to .csv file")
    matrix.to_csv('shortest_path.csv', index=False)


if __name__ == '__main__':
    main()
