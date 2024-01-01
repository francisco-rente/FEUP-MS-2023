import argparse
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import difflib
from unidecode import unidecode


def match_list_names(names_list, match_list):
    matched_names = {}
    for name in names_list:
        closest_name = max(match_list, key=lambda x: difflib.SequenceMatcher(None, x, name, autojunk=False).ratio())
        matched_names[name] = closest_name
    return matched_names


def group_validations_centroids(sections_df, validations_df, stops_df):
    validations_df['stop_name'] = match_list_names(validations_df['stop_name'], stops_df['stop_name']).values()
    stops_df['count'] = stops_df.groupby('stop_name')['stop_name'].transform('count')
    stops_df = stops_df.merge(validations_df, on='stop_name', how='left')
    
    centroid_validations_df = pd.DataFrame(columns=['section_id', 'validations'])

    for _, section_row in sections_df.iterrows():
        region_id = str(section_row['OBJECTID'])
        validations_count = 0

        # Iterate over the current section and its adjacent sections
        for _, stop_row in stops_df.iterrows():
            stop = Point(stop_row['stop_lon'], stop_row['stop_lat'])
            if stop.within(section_row['geometry']):
                validations_count += stop_row['validations'] / stop_row['count']

        # Check adjacent sections
        adjacent_sections = sections_df[sections_df.geometry.touches(section_row['geometry'])]
        for _, adjacent_section_row in adjacent_sections.iterrows():
            for _, stop_row in stops_df.iterrows():
                stop = Point(stop_row['stop_lon'], stop_row['stop_lat'])
                if stop.within(adjacent_section_row['geometry']):
                    validations_count += stop_row['validations'] / stop_row['count']

        centroid_validations_df = centroid_validations_df._append({'section_id': region_id, 'validations': validations_count}, ignore_index=True)
    
    return centroid_validations_df

    
def main():
    parser = argparse.ArgumentParser(description='Computes validations per sections.')
    parser.add_argument('--validations', type=str, nargs='+', help='PATH to one or more CSV files with validations info', required=True)
    parser.add_argument('--gtfs', type=str, nargs='+', help='PATH to one or more GTFS containing stops for each corresponding CSV files provided', required=True)
    parser.add_argument('--gpkg', type=str, help='PATH to a GPKG file with centroids to group stops to', required=True)
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    validations_paths = args.validations
    gtfs_paths = args.gtfs
    gpkg_path = args.gpkg
    output_path = args.output_path

    if len(validations_paths) != len(gtfs_paths):
        parser.error('The number of validation CSV paths and GTFS paths must be the same.')

    if not os.path.exists(gpkg_path):
        print(f'> GPKG path {gpkg_path} does not exist')
        exit(1)

    print(f'> Opening GPKG file {gpkg_path}')
    sections_df = gpd.read_file(gpkg_path).to_crs(epsg=4326)

    centroid_validations = []
    for validations_path, gtfs_path in zip(validations_paths, gtfs_paths):

        if not os.path.exists(validations_path):
            print(f'> Validations CSV file path {validations_path} does not exist')
            continue

        print(f'> Opening stops.txt GTFS file in {gtfs_path} DIR')
        stops_path = os.path.join(gtfs_path, 'stops.txt')

        if not os.path.exists(stops_path):
            print(f'> stops.txt file in DIR {gtfs_path} does not exist')
            continue

        print(f'> Opening validations file {validations_path}')
        validations_df = pd.read_csv(validations_path)
        stops_df = pd.read_csv(stops_path)
        stops_df['stop_name'] = stops_df['stop_name'].apply(unidecode)

        centroid_validations.append(group_validations_centroids(sections_df, validations_df, stops_df))

    print(f'> Merging centroid validations')
    merged_df = pd.concat(centroid_validations).groupby(['section_id']).sum().reset_index()
    merged_df['section_id'] = merged_df['section_id'].astype('int64')
    merged_df['validations'] = merged_df['validations'].astype('int64')

    print(f'> Writing results to {output_path}')
    merged_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
