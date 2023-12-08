import pickle
import os
import pandas as pd
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from utils import timed


@timed(__debug__)
def read_graph_pickle(file_path):
    return pickle.load(open(file_path, 'rb'))


def isCentroid(node):
    return node['type'] == 'centroid'


def extract_centroids_from_graph(G):
    return list(filter(lambda x: G.nodes[x]['type'] == 'centroid', G.nodes()))


@timed(__debug__)
def shortest_dijkstra_path(G, c1, c2):
    p = nx.dijkstra_path(G, c1, c2)
    d = sum([G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1)])
    return (c1, c2, '-'.join(p), str(d))


@timed(__debug__)
def shortest_astar_path(G, c1, c2):
    p = nx.astar_path(G, c1, c2, heuristic=lambda x, y: math.dist(G.nodes[x]['pos'], G.nodes[y]['pos'])) 
    d = sum([G[p[i]][p[i+1]]['weight'] for i in range(len(p)-1)])
    return (c1, c2, '-'.join(p), str(d))


def create_adjacency_matrix_file(G, centroids, file_path, num_paths=None):
    with ThreadPoolExecutor() as executor:      # NOTE: It will default to the number of processors on the machine, multiplied by 5

        if num_paths:
            print(f'> Submitting {num_paths} path(s) calculation(s)')
        else:
            num_centroids = len(centroids)
            print(f'> Submitting {num_centroids * num_centroids} path(s) calculation(s)')

        futures = []
        for c1 in centroids:
            for c2 in centroids:
                futures.append(executor.submit(shortest_astar_path, G, c1, c2))
                if num_paths and len(futures) >= num_paths: break
            if num_paths: break
        
        waiting = len(futures)
        completed = 0
        print(f'> Waiting for {waiting} results')
        with open(file_path, 'w') as f:
            f.write('id,from,to,path,distance\n')
            for completed_future in as_completed(futures):
                completed += 1
                f.write(f'{completed},{",".join(completed_future.result())}\n')     # NOTE: Flush is explicitly called after a newline
                f.flush()
                print(f'> Completed: {completed}/{waiting}')
    

def main():     # NOTE: Run python script with -O flag to disable DEBUG features (such as timed decorator)
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
    
    G = read_graph_pickle('graph.gpickle')
    
    centroids = extract_centroids_from_graph(G) 
    create_adjacency_matrix_file(G, centroids, 'shortest_path.csv', num_paths=20 if __debug__ else None)


if __name__ == '__main__':
    main()
