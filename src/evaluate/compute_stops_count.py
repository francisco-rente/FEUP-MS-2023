import argparse
import pandas as pd
import os


def main():
    parser = argparse.ArgumentParser(description='Computes a CSV file with a count of times each stop appears in the paths in the resultant CSV file of shortest paths calculations.')
    parser.add_argument('csv_path', type=str, help='PATH to CSV file')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    csv_path = args.csv_path
    output_path = args.output_path

    if not os.path.exists(csv_path):
        print("CSV file not found!")
        exit(1)

    df = pd.read_csv(csv_path)
    
    stop_count = {}
    for path in df['path']:
        for stop in path.split('-')[1:-1]:
            stop_count[stop] = stop_count.get(stop, 0) + 1

    result_df = pd.DataFrame(list(stop_count.items()), columns=['stop_id', 'count'])

    # min max scaler
    min_count = result_df['count'].min()
    delta_count = result_df['count'].max() - min_count
    result_df['importance'] = (result_df['count'] - min_count) / (delta_count)

    # Sort by count
    result_df = result_df.sort_values(by='count', ascending=False)
    
    result_df.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
