import argparse
import matplotlib.pyplot as plt
import networkx as nx
import pickle

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('graph_path', type=str, help='PATH to graph with routes')
    parser.add_argument('--routes', type=str, nargs='+', help='Filter routes (default: all)')
    args = parser.parse_args()

    graph_path = args.graph_path
    routes = args.routes

    print(f'> Reading graph: {graph_path}')
    with open(graph_path, 'rb') as f:
        G = pickle.load(f)

    if not routes:
        print('> Filtering all edges with routes')

        filtered_edges = [(u, v) for u, v, data in G.edges(data=True) if 'routes' in data]
        subgraph = G

    else:
        print(f'> Filtering edges with routes: {routes}')

        filtered_edges = []
        used_nodes = set()
        for u, v, data in G.edges(data=True):
            if 'routes' in data:
                for route in routes:    # For instance: --routes A B Bexp C D E F
                    if route in data['routes']:
                        filtered_edges.append((u, v))
                        used_nodes.add(u)
                        used_nodes.add(v)
                        break

        # Create a subgraph with only the filtered edges
        subgraph = G.subgraph(used_nodes)

    # Get the spatial layout
    pos = nx.get_node_attributes(subgraph, 'pos')

    # Swap x and y coordinates in the positions
    print('> Swapping pos')
    pos_swapped = {node: (y, x) for node, (x, y) in pos.items()}

    # Draw the subgraph
    print('> Drawing plot')
    nx.draw(subgraph, pos=pos_swapped, edgelist=filtered_edges, with_labels=True, node_size=50, node_color='skyblue', font_size=4, font_color='black')

    # Show the graph
    plt.show()


if __name__ == '__main__':
    main()
