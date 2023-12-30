import argparse
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import difflib


# Match each stop from GTFS to a stop in TIP validations
def match_stop_names(gtfs_stops_names, tip_validations_names):
    matched_names = [] 
    for gtfs_name in gtfs_stops_names:
        closest_name = max(tip_validations_names, key=lambda x: difflib.SequenceMatcher(None, x, gtfs_name).ratio())
        matched_names.append(closest_name)
    return matched_names


def match_with_gtfs_stops(gtfs_stops_file, df_tip_validations):

    # 

    df_gtfs_stops = pd.read_csv(gtfs_stops_file, delimiter=',')
    sections_df = gpd.read_file(SECTIONS_GPKG).to_crs(epsg=4326)

    df_tip_validations['stop_name'] = match_stop_names(df_gtfs_stops['stop_name'], df_tip_validations['stop_name'])

    df_tip_validations = df_tip_validations.merge(df_gtfs_stops[['stop_name', 'stop_lat', 'stop_lon']], on='stop_name', how='left')
 
    # New dataframe for centroid vals count
    df_centroids_vals_count = pd.DataFrame(columns=['section_id', 'validations'])

    for _, section_row in sections_df.iterrows():
        region_id = str(section_row['OBJECTID'])
        validations_count = 0
        for _, stop_row in df_tip_validations.iterrows():
            stop = Point(stop_row['stop_lon'], stop_row['stop_lat'])
            if stop.within(section_row['geometry']):
                validations_count += stop_row['Validações']

        df_centroids_vals_count = df_centroids_vals_count._append({'section_id': region_id, 'validations': validations_count}, ignore_index=True)
    
    return df_centroids_vals_count

    
def main():
    parser = argparse.ArgumentParser(description='Extracts validations from excel files into an output file (e.g. csv).')
    parser.add_argument('--validations', type=str, nargs='+', help='PATH to one or more CSV files with validations info', required=True)
    parser.add_argument('--gtfs', type=str, nargs='+', help='PATH to one or more GTFS containing stops for each corresponding CSV files provided', required=True)
    parser.add_argument('--gpkg', type=str, help='PATH to a GPKG file with centroids to group stops to', required=True)
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    validations_paths = args.validations
    gtfs_paths = args.gtfs
    gpkg_paths = args.gpkg
    output_path = args.output_path

    if len(validations_paths) != len(gtfs_paths):
        parser.error('The number of validation CSV paths and GTFS paths must be the same.')

    print("> Matching Metro stops with Centroids")
    df_centroids_metro_vals = match_with_gtfs_stops(METRO_GTFS_STOPS, df_metro_stop_count)
    df_centroids_stcp_vals = match_with_gtfs_stops(STCP_GTFS_STOPS, df_stcp_stop_count)

    # merge metro and stcp summing the validations per section
    print("> Merging Metro and STCP")
    df_merged = pd.concat([df_centroids_metro_vals, df_centroids_stcp_vals]).groupby(['section_id']).sum().reset_index()
    df_merged['section_id'] = df_merged['section_id'].astype('int64')
    df_merged['validations'] = df_merged['validations'].astype('int64')

    avg_distance_to_node = pd.read_csv(AVG_DISTANCE_TO_NODE_CSV)
    avg_distance_to_node.rename(columns={'to': 'section_id'}, inplace=True)  

    final_output  = avg_distance_to_node.merge(df_merged, on='section_id', how='right')
    final_output['indicator'] = final_output['validations'] * final_output['weight']
    final_output.to_csv(RESULT_FILE, index=False, header=True)


if __name__ == "__main__":
    main()
