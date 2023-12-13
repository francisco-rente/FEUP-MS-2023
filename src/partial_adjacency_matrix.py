import pickle
import os
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from utils import timed
import sys
import pandas as pd
import sys

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


def create_adjacency_matrix_file(G, group_pairs, file_path):
    previous_paths = os.path.exists(file_path)

    if previous_paths:
        print('> Detected previous file, filtering those already calculated')
        df = pd.read_csv(file_path, dtype={'from': str, 'to': str})
        group_pairs = group_pairs[~group_pairs.apply(lambda row: row['to'] in df[df['from'] == row['from']]['to'].values, axis=1)]
    
    with ThreadPoolExecutor() as executor:      # NOTE: It will default to the number of processors on the machine, multiplied by 5
        print(f'> Submitting {len(group_pairs)} path(s) calculation(s)')

        futures = []
        for _, row in group_pairs.iterrows():
            c1, c2 = row['from'], row['to']
            futures.append(executor.submit(shortest_astar_path, G, c1, c2))
            
        waiting = len(futures)
        completed = 0
        print(f'> Waiting for {waiting} results')
        
        with open(file_path, 'a') as f:
            if not previous_paths:
                f.write('from,to,path,weight\n')
            for completed_future in as_completed(futures):
                completed += 1
                f.write(f'{",".join(completed_future.result())}\n')
                f.flush()
                print(f'> Completed: {completed}/{waiting}')
    

def main():     # NOTE: Run python script with -O flag to disable DEBUG features (such as timed decorator)
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
    
    if len(sys.argv) != 4: 
        print("Usage: python src/compute_adjacency_matrix.py <num_groups> <group_id> <stop_id>")
        exit(1)

    stop_id = sys.argv[3]
    num_groups = int(sys.argv[1])
    group_id = int(sys.argv[2]) - 1
    G = read_graph_pickle(f'graph_without_{stop_id}.gpickle')

    df = pd.read_csv(f'../results/paths_affected_by_{stop_id}.csv', dtype={'from': str, 'to': str})

    #get all pairs of from and to
    df = df[['from', 'to']]
    
    #separate df in groups 
    group_size = len(df) // num_groups
    
    start_idx = group_id * group_size
    end_idx = (group_id + 1) * group_size if group_id < num_groups - 1 else len(df)
    group_pairs = df[start_idx:end_idx]

    create_adjacency_matrix_file(G, group_pairs, f'../results/shortest_path_no_{stop_id}_group_{group_id + 1}.csv')


if __name__ == '__main__':
    main()
