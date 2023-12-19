import pandas as pd
import os
import pickle
import networkx as nx


def main():
    if not os.path.exists('../results/shortest_paths.csv'):
        print("Results not found, please run compute_adjacency_matrix.py first!")
        exit(1)

    df = pd.read_csv('../results/shortest_paths.csv')
    G = pickle.load(open('graph.gpickle', 'rb'))
    edges = nx.get_edge_attributes(G, 'routes', default=[])

    for path in df['path']:
        stops = path.split('-')[1:-1]
        routes = []
        for i in range(len(stops) - 1):
            routes.append(set(edges[(stops[i], stops[i+1])]))


if __name__ == '__main__':
    main()
