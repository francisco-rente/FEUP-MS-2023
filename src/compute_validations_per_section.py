import argparse
import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import difflib
from unidecode import unidecode


def group_validations_centroids(sections_df, validations_df):
    centroid_validations_df = pd.DataFrame(columns=['section_id', 'validations'], dtype=int)

    for _, section_row in sections_df.iterrows():
        region_id = str(section_row['OBJECTID'])
        validations_count = 0

        # Iterate over the current section and its adjacent sections
        for _, stop_row in validations_df.iterrows():
            stop = Point(stop_row['stop_lon'], stop_row['stop_lat'])
            if stop.within(section_row['geometry']):
                validations_count += stop_row['validations']

        centroid_validations_df = centroid_validations_df._append({'section_id': region_id, 'validations': validations_count}, ignore_index=True)
    
    return centroid_validations_df

    
def main():
    parser = argparse.ArgumentParser(description='Computes validations per sections.')
    parser.add_argument('network_validations_path', type=str, help='PATH to one CSV files with validations info')
    parser.add_argument('gpkg_path', type=str, help='PATH to a GPKG file with centroids to group stops to')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    validations_path = args.network_validations_path
    gpkg_path = args.gpkg_path
    output_path = args.output_path

    if not os.path.exists(gpkg_path):
        print(f'> GPKG path {gpkg_path} does not exist')
        exit(1)

    print(f'> Opening GPKG file {gpkg_path}')
    sections_df = gpd.read_file(gpkg_path).to_crs(epsg=4326)

    print(f'> Opening validations file {validations_path}')
    validations_df = pd.read_csv(validations_path)

    centroid_validations = group_validations_centroids(sections_df, validations_df)

    print(f'> Writing results to {output_path}')
    centroid_validations.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
