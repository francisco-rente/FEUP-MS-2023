import pickle
import os
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from utils import timed
import sys
import pandas as pd


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


def create_adjacency_matrix_file(G, sources, targets, file_path, num_paths=None):
    previous_paths = os.path.exists(file_path)

    if previous_paths:
        print('> Detected previous file, filtering those already calculated')
        df = pd.read_csv(file_path, dtype={'from': str, 'to': str})
        paths_already_calculated = df.groupby('from')['to'].apply(set).to_dict()  # NOTE: Dict with {from: set(all_to)}

    with ThreadPoolExecutor() as executor:      # NOTE: It will default to the number of processors on the machine, multiplied by 5
        num_paths = num_paths or len(sources) * len(targets)
        print(f'> Submitting at most {num_paths} path(s) calculation(s)')

        futures = []
        for c1 in sources:
            for c2 in targets:
                if not (previous_paths and c2 in paths_already_calculated.get(c1, set())):
                    futures.append(executor.submit(shortest_astar_path, G, c1, c2))
                if len(futures) >= num_paths: break
            if len(futures) >= num_paths: break
        
        waiting = len(futures)
        completed = 0
        print(f'> Waiting for {waiting} results')
        
        with open(file_path, 'a') as f:
            if not previous_paths:
                f.write('from,to,path,distance\n')
            for completed_future in as_completed(futures):
                completed += 1
                f.write(f'{",".join(completed_future.result())}\n')
                f.flush()
                print(f'> Completed: {completed}/{waiting}')
    

def main():     # NOTE: Run python script with -O flag to disable DEBUG features (such as timed decorator)
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
    
    G = read_graph_pickle('graph.gpickle')
    
    centroids = extract_centroids_from_graph(G) 

    num_groups = int(sys.argv[1])
    group_size = len(centroids) // num_groups
    group_id = int(sys.argv[2]) - 1

    start_idx = group_id * group_size
    end_idx = (group_id + 1) * group_size if group_id < num_groups - 1 else len(centroids)
    group_centroids = centroids[start_idx:end_idx]

    create_adjacency_matrix_file(G, group_centroids, centroids, f'shortest_path_group_{group_id + 1}.csv', num_paths=20 if __debug__ else None)


if __name__ == '__main__':
    main()
