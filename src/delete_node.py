import argparse
import pickle
import os


def main():
    parser = argparse.ArgumentParser(description='Deletes a node from a graph.')
    parser.add_argument('graph_path', type=str, help='PATH to graph file')
    parser.add_argument('node_id', type=str, help='Node ID to be deleted from graph')
    parser.add_argument('output_path', type=str, help='PATH to output graph file')
    args = parser.parse_args()

    graph_path = args.graph_path
    node_id = args.node_id
    output_path = args.output_path

    if not os.path.exists(graph_path):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)

    with open(graph_path, 'rb') as f:
        G = pickle.load(f)

    # Verify if stop exists
    if node_id not in G.nodes():
        print(f"Stop {node_id} not found!")
        exit(1)

    G.remove_node(node_id) # Removes the node n and all adjacent edges. Attempting to remove a nonexistent node will raise an exception.

    # NOTE: Be careful with ouput_path! f'graph_without_{stop}.gpickle'
    with open(output_path, 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
