import argparse
import pandas as pd
import pickle
from tqdm import tqdm
import os


def analyse_path(G, path):
    distance = 0
    routes = []
    for i in range(len(path)-1):
        edge = G[path[i]][path[i+1]]
        distance += edge['distance']
        if 'routes' in edge:
            routes.append(set(edge['routes']))
        else:
            routes.append(set())
    return distance, routes


def main():
    parser = argparse.ArgumentParser(description='Computes distance and routes of shortest paths in a CSV file resultant of computing shortest paths.')
    parser.add_argument('graph_path', type=str, help='PATH to graph file')
    parser.add_argument('csv_path', type=str, help='PATH to CSV file')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    graph_path = args.graph_path
    csv_path = args.csv_path
    output_path = args.output_path

    if not os.path.exists(graph_path):
        print("Graph not found!")
        exit(1)

    if not os.path.exists(csv_path):
        print("CSV file not found!")
        exit(1)
    
    with open(graph_path, 'rb') as f:
        print('> Loading graph')
        G = pickle.load(f)

    df = pd.read_csv(csv_path)

    tqdm.pandas()
    
    print('> Calculating distances and routes')
    df[['distance', 'routes']] = df.progress_apply(lambda row: analyse_path(G, row['path'].split('-')), axis=1, result_type='expand')

    print('> Saving')
    df.to_csv(output_path, index=False) # NOTE: Before '../results/shortest_paths_with_basic_statistics.csv'


if __name__ == '__main__':
    main()
