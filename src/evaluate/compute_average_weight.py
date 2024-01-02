import argparse
import pandas as pd
import os


def main():
    parser = argparse.ArgumentParser(description='Computes the average weight of all paths in shortest path CSV file.')
    parser.add_argument('csv_path', type=str, help='PATH to CSV file')
    args = parser.parse_args()

    csv_path = args.csv_path

    if not os.path.exists(csv_path):
        print("CSV file not found!")
        exit(1)

    df = pd.read_csv(csv_path)
    
    print(df['weight'].mean())


if __name__ == '__main__':
    main()
