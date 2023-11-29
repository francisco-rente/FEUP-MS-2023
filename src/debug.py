import pickle

with open('routes.gpickle', 'rb') as f:
    G = pickle.load(f)

for from_stop, to_stop, data in G.edges(data=True):
    if len(set(data['routes'])) != len(data['routes']):
        print(from_stop, to_stop, data['routes'])

print([(node, data) for node, data in G.nodes.items() if data['pos'][1] < 41])