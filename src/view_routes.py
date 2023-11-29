import matplotlib.pyplot as plt
import networkx as nx
import pickle

with open('routes.gpickle', 'rb') as f:
    G = pickle.load(f)

# Draw the graph with spatial layout
nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True, node_size=50, node_color='skyblue', font_size=4, font_color='black')

# Show the graph
plt.show()