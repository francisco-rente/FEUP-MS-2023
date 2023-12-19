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
    
    with open(output_path, 'w') as f:
        f.write('stop,count\n')
        for key, value in stop_count.items():
            f.write(f'{key},{value}\n')


if __name__ == '__main__':
    main()
