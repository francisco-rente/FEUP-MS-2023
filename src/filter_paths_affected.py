import pandas as pd
import os
import sys


SHORTEST_PATHS_PATH = '../results/shortest_paths.csv'


def main():
    stop = sys.argv[1]
    if not os.path.exists(SHORTEST_PATHS_PATH):
        print("Results not found, please run compute_adjacency_matrix.py first!")
        exit(1)
    adj_matrix_df = pd.read_csv(SHORTEST_PATHS_PATH)
    stop_rows = adj_matrix_df[adj_matrix_df['path'].str.contains(stop)]
    stop_rows.to_csv(f'../results/paths_affected_by_{stop}.csv', index=False)


if __name__ == '__main__':
    main()
