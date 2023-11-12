import pickle
import pandas as pd
import networkx as nx
import matplotlib.pyplot as plt
import geopandas as gpd
import contextily as ctx
import folium
import osmnx as ox
import osmium as osm

SECTIONS_GPKG = "../datasets/BGRI2021_1312.gpkg"
DEGREE_TO_METER = 111139
STCP_SHAPE = "../datasets/gtfs-stcp/shapes.txt"

def draw_graph_nx(G):
    print('Drawing graph...')
    colors = {'Centroid': 'red', 'Stop': 'blue'}
    color_values = [colors.get(G.nodes[node]['type'], 'skyblue') for node in G.nodes()]

    nx.draw(G, nx.get_node_attributes(G, 'pos'), with_labels=True,\
        node_size=50, node_color=color_values, font_size=8, font_color='black',\
            edge_color='grey', width=0.5, alpha=0.7)
    plt.show()


def draw_graph_contextly(G):
    gd_df = gpd.read_file(SECTIONS_GPKG)
    ax = gd_df.plot(alpha=0.4, color='grey', figsize=(50, 50))
    gd_df = gd_df.to_crs(epsg=4326)
    # draw graph
    draw_graph_nx(G)

    ctx.add_basemap(ax, source=ctx.providers.CartoDB.Positron, crs=gd_df.crs.to_string())

    ax.set_aspect('equal')
    ax.set_axis_off()
    plt.show()

def folium_map(G, route_shapes):
    df = gpd.read_file(SECTIONS_GPKG)

    # get shape bouding box
    minx, miny, maxx, maxy = df.total_bounds
    print(minx, miny, maxx, maxy)

    df = df.to_crs(epsg=4326)
    m = folium.Map(location=[41.15, -8.61024], tiles="CartoDB positron", zoom_start=12)

    for _, r in df.iterrows():
        sim_geo = gpd.GeoSeries(r["geometry"])
        geo_j = sim_geo.to_json()
        geo_j = folium.GeoJson(data=geo_j, style_function=lambda x: {
                               "fillColor": "orange"})
        folium.Popup(r["OBJECTID"]).add_to(geo_j)
        geo_j.add_to(m)

   
    conversion = lambda x, y: (y, x)

    for node in G.nodes():
        folium.CircleMarker(location=conversion(G.nodes[node]['pos'][0], G.nodes[node]['pos'][1]),\
                            radius=2, fill=True,\
                            color='red' if G.nodes[node]['type'] == 'Centroid' else 'blue').add_to(m)

    for edge in G.edges():
        folium.PolyLine(locations=[conversion(G.nodes[edge[0]]['pos'][0], G.nodes[edge[0]]['pos'][1]),\
                                  conversion(G.nodes[edge[1]]['pos'][0], G.nodes[edge[1]]['pos'][1])],\
                        color='grey', weight=1).add_to(m)
    
    for _, r in route_shapes.iterrows():
#        print(r['shape_pt_sequence'])
        folium.PolyLine(locations=r['shape_pt_sequence'],\
                        color='green', weight=3).add_to(m)

    # add routes polylines

    m.save("map.html")


def read_shapes_and_extract_polylines(df):
    print('Reading shapes and extracting polylines...')

    # for each shape_id, create a list of (lat, lon) tuples
    df_route = pd.DataFrame()
    for shape_id in df['shape_id'].unique():
        df_route = df_route._append({'shape_id': shape_id,\
                'shape_pt_sequence': list(zip(\
                    df[df['shape_id'] == shape_id]['shape_pt_lat'], 
                    df[df['shape_id'] == shape_id]['shape_pt_lon']))},\
                ignore_index=True)
    
    return df_route


def bus_routes_from_osm():
#    place_name = "Porto, Portugal"
#    routes_geojson = gpd.read_file("./export.geojson")
    pass 


def remove_centroid_edges(G):
    print('Removing centroid edges...')
    l = [(u, v) for u, v in G.edges(data=False) \
        if 'type' in G.nodes[u] and G.nodes[u]['type'] == 'Centroid']
    G.remove_edges_from(l)
    return G


def main():
    with open('routes_centroids.gpickle', 'rb') as f:
        G = pickle.load(f)
    G = remove_centroid_edges(G)
    stcp_shapes = pd.read_csv(STCP_SHAPE, sep=',')
    stcp_shapes = read_shapes_and_extract_polylines(stcp_shapes)
    folium_map(G, stcp_shapes)


if __name__ == '__main__':
    main()
