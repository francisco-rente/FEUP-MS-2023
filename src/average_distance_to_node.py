import pandas as pd


file_path = './results/shortest_paths.csv'

df = pd.read_csv(file_path)

average_weight = df.groupby('to')['weight'].mean()

average_weight.to_csv('./results/average_distance_to_node.csv', index=True, header=True)
