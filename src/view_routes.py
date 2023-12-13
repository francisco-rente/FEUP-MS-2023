import matplotlib.pyplot as plt
import networkx as nx
import pickle

print('> Opening pickle')
with open('graph_without_5726.gpickle', 'rb') as f:
    G = pickle.load(f)

# Get the spatial layout
pos = nx.get_node_attributes(G, 'pos')

# Swap x and y coordinates in the positions
print('> Swapping pos')
pos_swapped = {node: (y, x) for node, (x, y) in pos.items()}

# Extract edges with the "routes" attribute
print('> Filtering edges')
#filtered_edges = [(u, v) for u, v, data in G.edges(data=True) if 'routes' in data]
filtered_edges = []
for u, v, data in G.edges(data=True):
    if 'routes' in data:
        for route in ['A', 'B', 'Bexp', 'C', 'D', 'E', 'F']:
            if route in data['routes']:
                filtered_edges.append((u, v))
                break

# Draw the graph with swapped x and y axes, showing only edges with "routes" attribute
print('> Drawing plot')
nx.draw(G, pos=pos_swapped, edgelist=filtered_edges, with_labels=True, node_size=50, node_color='skyblue', font_size=4, font_color='black')

# Show the graph
plt.show()
