import argparse
import os
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description='Creates a CSV with average weight to all sections from all sections.')
    parser.add_argument('csv_path', type=str, help='PATH to the CSV file resultant of computing shortest paths')
    parser.add_argument('output_path', type=str, help='PATH to output CSV file')
    args = parser.parse_args()

    csv_path = args.csv_path
    output_path = args.output_path

    if not os.path.exists(csv_path):
        print("Results not found!")
        exit(1)

    df = pd.read_csv(csv_path)
    average_weight = df.groupby('to')['weight'].mean().reset_index()
    average_weight.rename(columns={'to': 'section_id'}, inplace=True)
    average_weight.to_csv(output_path, index=False)


if __name__ == '__main__':
    main()
