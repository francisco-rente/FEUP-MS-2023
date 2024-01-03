import argparse
import os
import pandas as pd


def main(): 
    parser = argparse.ArgumentParser(description='Joins validations with id .')
    parser.add_argument('validations_with_ids', type=str, help='PATH to the CSV file resultant of merging validations from excel with stops from gtfs')
    parser.add_argument('stop_counts', type=str, help='PATH to the CSV file that contains the stop counts and importance for each stop_id')
    args = parser.parse_args()

    validations_id_path = args.validations_with_ids
    stop_counts_path = args.stop_counts

    if not os.path.exists(validations_id_path):
        print('Validations with identifiers file not found!')
        exit(1)

    if not os.path.exists(stop_counts_path):
        print('Stop count information file not found!')
        exit(1)

    validations_ids = pd.read_csv(validations_id_path)
    stop_counts = pd.read_csv(stop_counts_path)

    result_df = pd.merge(stop_counts, validations_ids, on='stop_id')

    max_validations = result_df['validations'].max()
    min_validations = result_df['validations'].min()
    delta_validations = max_validations - min_validations

    result_df['validations'] = (result_df['validations'] - min_validations) / delta_validations
    
    print(f'corr: {result_df["validations"].corr(result_df["importance"])}')
    print(f'cov: {result_df["validations"].cov(result_df["importance"])}')
    print(result_df[['importance', 'validations']].describe())


if __name__ == '__main__': 
    main()