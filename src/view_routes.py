import matplotlib.pyplot as plt
import networkx as nx
import pickle

with open('routes.gpickle', 'rb') as f:
    G = pickle.load(f)

# Get the spatial layout
pos = nx.get_node_attributes(G, 'pos')

# Swap x and y coordinates in the positions
pos_swapped = {node: (y, x) for node, (x, y) in pos.items()}

# Extract edges with the "routes" attribute
filtered_edges = [(u, v) for u, v, data in G.edges(data=True) if 'routes' in data]

# Draw the graph with swapped x and y axes, showing only edges with "routes" attribute
nx.draw(G, pos=pos_swapped, with_labels=True, node_size=50, node_color='skyblue', font_size=4, font_color='black', edgelist=filtered_edges)

# Show the graph
plt.show()
