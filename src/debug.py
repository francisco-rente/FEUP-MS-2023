import pickle
import os
import networkx as nx


def main():
    if not os.path.exists('graph.gpickle'):
        print("Graph not found, please run generate_routes_graph.py first!")
        exit(1)
    
    G = pickle.load(open('graph.gpickle', 'rb'))

    print(nx.is_strongly_connected(G))


if __name__ == '__main__':
    main()
