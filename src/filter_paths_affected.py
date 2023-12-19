import argparse
import pandas as pd
import os


def main():
    parser = argparse.ArgumentParser(description='Filter affected paths by the hypothetical removal of a stop.')
    parser.add_argument('csv_path', type=str, help='PATH to the CSV file resultant of computing shortest paths')
    parser.add_argument('stop_id', type=str, help="Stop ID to check it's influence when removed")
    parser.add_argument('output_path', type=str, help='PATH to output CSV file')
    args = parser.parse_args()

    csv_path = args.csv_path
    stop_id = args.stop_id
    output_path = args.output_path

    if not os.path.exists(csv_path):
        print("Results not found!")
        exit(1)
    
    adj_matrix_df = pd.read_csv(csv_path)
    stop_rows = adj_matrix_df[adj_matrix_df['path'].str.contains(stop_id)]
    stop_rows.to_csv(output_path, index=False)  # NOTE: f'../results/paths_affected_by_{stop}.csv'


if __name__ == '__main__':
    main()
