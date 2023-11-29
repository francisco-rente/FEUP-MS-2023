import pickle
import geopandas as gpd
import math

SECTIONS_GPKG = "../datasets/BGRI2021_1312.gpkg"
DEGREE_TO_METER = 111139

def read_sections_file():

    print(f'> Reading {SECTIONS_GPKG} file...')

    df = gpd.read_file(SECTIONS_GPKG)
    df = df.to_crs(epsg=4326) # WGS 84 coordinate system
  
    return df

def extract_centroids(df):
    df = df.to_crs(epsg=2263)
    df["centroid"] = df.centroid
    df = df.to_crs(epsg=4326)
    df["centroid"] = df["centroid"].to_crs(epsg=4326)
    
    centroids = []
    print(f'> Extracting centroids...')
    for _, r in df.iterrows():
        lat = r["centroid"].x
        lon = r["centroid"].y
        region_id = r["OBJECTID"]
        centroids.append((region_id, lat, lon))
    
    return centroids

def insert_centroids_in_the_the_graph(G, centroids):
    for c in centroids:
        G.add_node(c[0], pos=(c[1], c[2]), type="Centroid")

        for n in G.nodes:
            dist = math.sqrt(((G.nodes[n]["pos"][0] - c[1]) * DEGREE_TO_METER) ** 2 + ((G.nodes[n]["pos"][1] - c[2]) * DEGREE_TO_METER) ** 2)
            G.add_edge(c[0], n, weight=dist, length=0, routes=[])
         
    return G


def main(): 
    with open('routes.gpickle', 'rb') as f:
        G = pickle.load(f)

    df = read_sections_file()
    centroids = extract_centroids(df)
    G = insert_centroids_in_the_the_graph(G, centroids)
    
    with open('routes_centroids.gpickle', 'wb') as f:
        pickle.dump(G, f)
    

if __name__ == '__main__':
    main()
