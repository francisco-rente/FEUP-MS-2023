import argparse
import os
import pandas as pd
from unidecode import unidecode


def read_excel_files(excel_dir_path):
    for filename in os.listdir(excel_dir_path):
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(excel_dir_path, filename)
            xls = pd.ExcelFile(file_path)
            dfs = []
            for sheet_name in xls.sheet_names:
                print(f'> Sheet Name : {sheet_name}')
                df = xls.parse(sheet_name)
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                dfs.append(df)             
            combined_df = pd.concat(dfs, ignore_index=True)
    return combined_df

    
def main():
    parser = argparse.ArgumentParser(description='Extracts validations from excel files into an output file (e.g. csv).')
    parser.add_argument('excel_dir_path', type=str, help='PATH to an excel file with validations info')
    parser.add_argument('stops_name_col', type=str, help='Column name of stop names corresponding to each excel file provided')
    parser.add_argument('validations_col', type=str, help='Column name of validations corresponding to each excel file provided')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    excel_dir_path = args.excel_dir_path
    stops_name_col = args.stops_name_col
    validations_col = args.validations_col
    outfile_path = args.output_path

    if not os.path.exists(excel_dir_path):
        print(f'> Validations excel file {excel_dir_path} not found')
        exit(1)

    df = read_excel_files(excel_dir_path)

    # Rename validations and stop names columns
    df.rename(columns={stops_name_col: 'stop_name', validations_col: 'validations'}, inplace=True)

    # Remove invalid validations (e.g. those who're not numeric) and NaN stop names
    df[validations_col] = pd.to_numeric(df['validations'], errors='coerce')
    df['stop_name'] = df['stop_name'].str.strip()
    df = df.dropna(subset=['stop_name', 'validations'])

    # Apply unidecode to stop names and remove unnecessary white spaces in the middle
    df['stop_name'] = df['stop_name'].apply(lambda x: ''.join(unidecode(x).split()))

    # Sum validations for same stop name
    df = df.groupby('stop_name')['validations'].sum().reset_index()

    # Convert validations to int64 type
    df['validations'] = df['validations'].astype('int64')

    df.to_csv(outfile_path, columns=['stop_name', 'validations'], index=False)


if __name__ == "__main__":
    main()
