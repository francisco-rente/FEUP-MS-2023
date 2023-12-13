import pandas as pd
import pickle

PATH = '../results/shortest_paths.csv'

def distance_from_path(G, path):
    return sum([G[path[i]][path[i+1]]['distance'] for i in range(len(path)-1)])
    

def get_routes(G, row): 
    path = row['path']
    routes = []
    for i in range(len(path)-1):
        edge = G[path[i]][path[i+1]]
        if 'routes' in edge:
            routes += edge['routes']
    return list(set(routes))





def main(): 
    df = pd.read_csv(PATH)
    with open('graph.gpickle', 'rb') as f:
        print('> Loading graph')
        G = pickle.load(f)
    
    df["path"] = df.apply(lambda row: row['path'].split('-'), axis=1)

    print('> Calculating distances')
    df["distance"] = df.apply(lambda row: distance_from_path(G, row['path']), axis=1)


    df["p_of_routes_to_stops"] = df.apply(lambda row: len(row['path']) / len(row['routes']), axis=1)


    df["path"] = df.apply(lambda row: '-'.join(row['path']), axis=1)

    #print('> Saving distances')
    #df.to_csv('../results/shortest_paths_with_distances.csv', index=False)

    print('> Calculating routes')
    df['routes']= df.apply(lambda row: get_routes(G, row), axis=1)
    
    routes = {}
    for _, row in df.iterrows():
        for route in row['routes']:
            routes[route] = routes.get(route, 0) + 1
    print('> Most used routes')
    print(sorted(routes.items(), key=lambda x: x[1], reverse=True)[:10])

    print('> Saving')
    df.to_csv('../results/shortest_paths_with_basic_statistics.csv', index=False)

if __name__ == '__main__':
    main()