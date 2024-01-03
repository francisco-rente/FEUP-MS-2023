import argparse
import os
import pandas as pd
import difflib
from unidecode import unidecode


def match_list_names(names_list, match_list):
    matched_names = {}
    for name in names_list:
        closest_name = max(match_list, key=lambda x: difflib.SequenceMatcher(None, x, name, autojunk=False).ratio())
        matched_names[name] = closest_name
    return matched_names
    

def main():
    parser = argparse.ArgumentParser(description='Match validations stop names with their IDs in the GTFS file.')
    parser.add_argument('--validations', type=str, nargs='+', help='PATH to one or more CSV files with validations info', required=True)
    parser.add_argument('--gtfs', type=str, nargs='+', help='PATH to one or more GTFS containing stops for each corresponding CSV files provided', required=True)
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    validations_paths = args.validations
    gtfs_paths = args.gtfs
    output_path = args.output_path

    if len(validations_paths) != len(gtfs_paths):
        parser.error('The number of validation CSV paths and GTFS paths must be the same.')

    result_df = pd.DataFrame()
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
        stops_df['stop_name'] = stops_df['stop_name'].apply(lambda x: ''.join(unidecode(x).split()))

        validations_df['stop_name'] = match_list_names(validations_df['stop_name'], stops_df['stop_name']).values()
        stops_df['count'] = stops_df.groupby('stop_name')['stop_name'].transform('count')
        stops_df = pd.merge(stops_df, validations_df, on='stop_name', how='left')
        stops_df['validations'] = stops_df['validations'] // stops_df['count']

        # Fill NaN values in 'validations' column with the average of non-NaN values
        average_validations = stops_df['validations'].mean()
        stops_df['validations'] = stops_df['validations'].fillna(average_validations)

        result_df = pd.concat([result_df, stops_df])

    result_df['validations'] = result_df['validations'].astype(int)

    print(f'> Writing results to {output_path}')
    result_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
