import sys
import pickle
import os


def main(): 
    stop = sys.argv[1]

    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)

    with open('graph.gpickle', 'rb') as f:
        G = pickle.load(f)

    # verify if stop exists
    if stop not in G.nodes():
        print(f"Stop {stop} not found!")
        exit(1)

    G.remove_node(stop) # Removes the node n and all adjacent edges. Attempting to remove a nonexistent node will raise an exception.

    with open(f'graph_without_{stop}.gpickle', 'wb') as f:
        pickle.dump(G, f, pickle.HIGHEST_PROTOCOL)


if __name__ == '__main__':
    main()
