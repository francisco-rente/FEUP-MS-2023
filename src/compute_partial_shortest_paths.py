import argparse
import pickle
import os
import networkx as nx
from concurrent.futures import ThreadPoolExecutor, as_completed
import math
from utils.utils import timed
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
    parser = argparse.ArgumentParser(description='Computes a CSV file with an adjacency matrix of shortest paths and weights from the pairs in the given CSV file.')
    parser.add_argument('graph_path', type=str, help='PATH to graph file')
    parser.add_argument('csv_path', type=str, help='PATH to CSV file with pairs of centroids')
    parser.add_argument('--batch', type=int, nargs=2, metavar=('BATCHES', 'BATCH_NUM'), help='Number of batches and batch number (in this order)')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    graph_path = args.graph_path
    csv_path = args.csv_path
    output_path = args.output_path

    if args.batch:
        batches, batch_num = args.batch
    else:
        batches, batch_num = (1, 1)

    if not os.path.exists(graph_path):
        print("Graph not found!")
        exit(1)

    if not os.path.exists(csv_path):
        print("CSV file not found!")
        exit(1)

    if batches < batch_num:
        print("Number of batches must be higher than batch number.")
        exit(1)

    num_groups = batches
    group_id = batch_num - 1
    G = read_graph_pickle(graph_path)   # NOTE: Before f'graph_without_{stop_id}.gpickle'

    df = pd.read_csv(csv_path, dtype={'from': str, 'to': str})  # NOTE: Before f'../results/paths_affected_by_{stop_id}.csv'

    # Get all pairs of from and to
    df = df[['from', 'to']]
    
    # Separate df in groups 
    group_size = len(df) // num_groups
    
    start_idx = group_id * group_size
    end_idx = (group_id + 1) * group_size if group_id < num_groups - 1 else len(df)
    group_pairs = df[start_idx:end_idx]

    create_adjacency_matrix_file(G, group_pairs, output_path)  # NOTE: Before f'../results/shortest_path_no_{stop_id}_group_{group_id + 1}.csv'


if __name__ == '__main__':
    main()
