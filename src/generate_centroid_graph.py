import matplotlib.pyplot as plt
import networkx as nx
import pickle
import os
import folium
import geopandas as gpd
import math
import contextily as ctx
import cartopy.crs as ccrs

data_dir = "../datasets/"
sections_gpkg = os.path.join(data_dir, "BGRI2021_1312.gpkg")

DEGREE_TO_METER = 111139

def read_sections_file():

    print(f'> Reading {sections_gpkg} file...')
    df = gpd.read_file(sections_gpkg)

    # Use WGS 84 (epsg:4326) as the geographic coordinate system
    df = df.to_crs(epsg=4326)

    # Porto -> Latitude: 41.15, Longitude: -8.61024
    m = folium.Map(location=[41.15, -8.61024],
                   zoom_start=10, tiles="CartoDB positron")
    
    print(f'> Extracting {sections_gpkg} file...')
    for _, r in df.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"])
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {
                               "fillColor": "orange"})
        folium.Popup(r["OBJECTID"]).add_to(geo_j)
        geo_j.add_to(m)

    
    return (m, df)

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
        print(f'> Inserting centroid {c[0]} in the graph...')
        G.add_node(c[0], pos=(c[1], c[2]), type="Centroid")


        count = 1
        for n in G.nodes:
            if n == c[0]:
                continue
            if count > 15: 
                break
            count += 1
            dist = math.sqrt(((G.nodes[n]["pos"][0] - c[1]) * DEGREE_TO_METER) ** 2 + ((G.nodes[n]["pos"][1] - c[2]) * DEGREE_TO_METER) ** 2)
            G.add_edge(c[0], n, weight=dist, length=0, routes=[])
         
    return G


def draw_centroids(df, m):
    df = df.to_crs(epsg=2263)
    df["centroid"] = df.centroid
    # geometry (active) column
    df = df.to_crs(epsg=4326)
    # Centroid column
    df["centroid"] = df["centroid"].to_crs(epsg=4326)

    for _, r in df.iterrows():
        lat = r["centroid"].x
        lon = r["centroid"].y
        folium.Marker(location=[lat, lon],
                      popup="OBJECTID: {}".format(r["OBJECTID"])).add_to(m)

    return (m, df)


def main(): 
    with open('routes.gpickle', 'rb') as f:
        G = pickle.load(f)
    (m, df) = read_sections_file()
    centroids = extract_centroids(df)
    G = insert_centroids_in_the_the_graph(G, centroids)
    print(f'> Drawing graph...')
    
    nx.draw(G, nx.get_node_attributes(G, 'pos'), node_size=1)
    fig = plt.figure(figsize=(30,21))
    ax = plt.axes(projection=ccrs.PlateCarree())
    ctx.add_basemap(ax, crs=df.crs.to_string())
    plt.show()
    

if __name__ == '__main__':
    main()
