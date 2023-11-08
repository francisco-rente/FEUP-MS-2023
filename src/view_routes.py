import matplotlib.pyplot as plt
import networkx as nx
import pandas as pd
import pickle

stops_df = pd.read_csv('../datasets/gtfs-stcp/stops.txt')

# Create a spatial layout based on stop coordinates
pos = {stop_id: (lon, lat) for stop_id, lat, lon in zip(stops_df['stop_id'], stops_df['stop_lat'], stops_df['stop_lon'])}

with open('routes.gpickle', 'rb') as f:
    G = pickle.load(f)

# Draw the graph with spatial layout
nx.draw(G, pos, with_labels=True, node_size=100, node_color='skyblue', font_size=8, font_color='black', font_weight='bold')

# Show the graph
plt.show()