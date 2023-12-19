import pandas as pd
import pickle
from tqdm import tqdm


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
    df = pd.read_csv('../results/shortest_paths.csv')
    with open('graph.gpickle', 'rb') as f:
        print('> Loading graph')
        G = pickle.load(f)

    tqdm.pandas()
    
    print('> Calculating distances and routes')
    df[['distance', 'routes']] = df.progress_apply(lambda row: analyse_path(G, row['path'].split('-')), axis=1, result_type='expand')

    print('> Saving')
    df.to_csv('../results/shortest_paths_with_basic_statistics.csv', index=False)


if __name__ == '__main__':
    main()
