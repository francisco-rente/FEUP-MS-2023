import argparse
import os
import pandas as pd


def main():
    parser = argparse.ArgumentParser(description='Computes an indicator of service of public transports with validations per section file and average weight to section file.')
    parser.add_argument('validations_path', type=str, help='PATH to validations per section CSV file')
    parser.add_argument('average_path', type=str, help='PATH average weight to section CSV file')
    parser.add_argument('output_path', type=str, help='PATH to output file')
    args = parser.parse_args()

    validations_path = args.validations_path
    average_path = args.average_path
    output_path = args.output_path

    if not os.path.exists(validations_path):
        print(f'> Validations per section file path {validations_path} does not exist')
        exit(1)

    if not os.path.exists(average_path):
        print(f'> Average weight to section file path {validations_path} does not exist')
        exit(1)

    validations_per_section_df = pd.read_csv(validations_path)
    avg_weight_to_section_df = pd.read_csv(average_path)

    result_df = avg_weight_to_section_df.merge(validations_per_section_df, on='section_id', how='right')
    result_df['indicator'] = (result_df['validations'] + 1) * result_df['weight']
    result_df['indicator_norm'] = (result_df['indicator'] - result_df['indicator'].min()) / (result_df['indicator'].max() - result_df['indicator'].min())
    result_df = result_df.sort_values(by='validations', axis=0, ascending=False)

    result_df.to_csv(output_path, index=False)


if __name__ == "__main__":
    main()
