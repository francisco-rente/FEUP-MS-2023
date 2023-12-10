import pandas as pd
import os


SHORTEST_PATHS_PATH = '../results/shortest_paths.csv'


def main():
    if os.path.exists(SHORTEST_PATHS_PATH):
        print("Results not found, please run compute_adjacency_matrix.py first!")
        exit(1)

    df = pd.read_csv(SHORTEST_PATHS_PATH)
    
    stop_count = {}
    for path in df['path']:
        for stop in path.split('-'):
            stop_count[stop] = stop_count.get(stop, 0) + 1
    
    with open('stops_count.csv', 'w') as f:
        f.write('stop,count\n')
        for key, value in stop_count.items():
            f.write(f'{key},{value}\n')


if __name__ == '__main__':
    main()
