import csv
from tqdm import tqdm

def find_missing_pairs(file1, file2):
    # Read data from the first CSV file
    with open(file1, 'r') as f1:
        reader1 = csv.DictReader(f1)
        data1 = {(row['from'], row['to']): row for row in reader1}

    # Read data from the second CSV file
    with open(file2, 'r') as f2:
        reader2 = csv.DictReader(f2)
        data2 = {(row['from'], row['to']) for row in reader2}

    # Find missing pairs in the first file
    missing_pairs = [data1[pair] for pair in tqdm(set(data1.keys()) - data2, desc='Processing', unit='row')]

    # Write missing pairs to the second file
    with open(file2, 'a', newline='') as f2:
        writer = csv.DictWriter(f2, fieldnames=reader1.fieldnames)
        if not data2:
            writer.writeheader()  # Write header if the second file is empty
        for row in tqdm(missing_pairs, desc='Writing', unit='row'):
            writer.writerow(row)


if __name__ == "__main__":
    file1_path = 'results/shortest_paths_raw.csv'  # Replace with the path to your first CSV file
    file2_path = 'results/shortest_paths_without_5726.csv'  # Replace with the path to your second CSV file

    find_missing_pairs(file1_path, file2_path)