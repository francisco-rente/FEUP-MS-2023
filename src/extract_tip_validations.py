import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import difflib


SECTIONS_GPKG = "./datasets/BGRI2021_1312.gpkg"
METRO_GTFS_STOPS = "./datasets/gtfs-mdp/stops.txt"
STCP_GTFS_STOPS = "./datasets/gtfs-stcp/stops.txt"
METRO_EXCEL_PATH = "./datasets/TIP_Validations/Porto Digital Ferrov 2022"
STCP_EXCEL_PATH = "./datasets/TIP_Validations/Porto Digital Rodov 2022"

METRO_EXCEL_DF = "./results/metro_excel_dataframe.csv"
STCP_EXCEL_DF = "./results/stcp_excel_dataframe.csv"
RESULT_FILE = './results/validation_per_section.csv'
AVG_DISTANCE_TO_NODE_CSV = './results/average_distance_to_node.csv'


def read_excel_files(dir_path):
    for filename in os.listdir(dir_path):
        if filename.endswith(".xlsx") or filename.endswith(".xls"):
            file_path = os.path.join(dir_path, filename)
            xls = pd.ExcelFile(file_path)
            dfs = {} 
            for sheet_name in xls.sheet_names:
                print(f'Sheet Name : {sheet_name}')
                df = xls.parse(sheet_name)
                df['Validações'] = pd.to_numeric(df['Validações'], errors='coerce')
                df = df.dropna(subset=['Validações'])
                df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
                print(df.columns)
                dfs[sheet_name] = df                
            combined_df = pd.concat(dfs.values(), ignore_index=True)
    return combined_df


def count_vals_by_stop(df):
    return df.groupby("stop_name").agg({"Validações": "sum"}).reset_index()


# TODO: Do we do this for every name or just NA
def match_stop_names(gtfs_stops_names, tip_validations_names):
    matched_names = [] 
    for tip_name in tip_validations_names:
        closest_name = max(gtfs_stops_names, key=lambda x: difflib.SequenceMatcher(None, x, tip_name).ratio())
        matched_names.append(closest_name)
    return matched_names


def match_with_gtfs_stops(gtfs_stops_file, df_tip_validations):

    df_gtfs_stops = pd.read_csv(gtfs_stops_file, delimiter=',')
    sections_df = gpd.read_file(SECTIONS_GPKG).to_crs(epsg=4326)

    df_tip_validations['stop_name'] = match_stop_names(df_gtfs_stops['stop_name'], df_tip_validations['stop_name'])

    df_tip_validations = df_tip_validations.merge(df_gtfs_stops[['stop_name', 'stop_lat', 'stop_lon']], on='stop_name', how='left')

    # New dataframe for centroid vals count
    df_centroids_vals_count = pd.DataFrame(columns=['section_id', 'validations'])

    for _, section_row in sections_df.iterrows():
        region_id = str(section_row['OBJECTID'])
        validations_count = 0
        for _, stop_row in df_tip_validations.iterrows():
            stop = Point(stop_row['stop_lon'], stop_row['stop_lat'])
            if stop.within(section_row['geometry']):
                validations_count += stop_row['Validações']

        df_centroids_vals_count = df_centroids_vals_count._append({'section_id': region_id, 'validations': validations_count}, ignore_index=True)
    
    return df_centroids_vals_count

    
def main():
    if os.path.exists(RESULT_FILE):
        print("> Section Validations already calculated")

    # metro 

    print("> Reading Metro TIP files")
    if not os.path.exists(METRO_EXCEL_DF):
        df_metro_excel = read_excel_files(METRO_EXCEL_PATH) 
        df_metro_excel.rename(columns={'Est/Op' : 'stop_name'}, inplace=True)
        df_metro = df_metro_excel[~df_metro_excel['stop_name'].str.startswith('CP-')].copy()
        df_metro.to_csv(METRO_EXCEL_DF, index=False, header=True) #TODO: do after name matching with stops.txt? 
    else: 
        df_metro = pd.read_csv(METRO_EXCEL_DF)

    print("> Counting Metro Stop Validation")
    df_metro_stop_count = count_vals_by_stop(df_metro)
    
    print("Number of lines in df_metro_stop_count:", df_metro_stop_count.shape[0])

    print("> Matching Metro stops with Centroids")
    df_centroids_metro_vals = match_with_gtfs_stops(METRO_GTFS_STOPS, df_metro_stop_count)

    # stcp

    print("> Reading STCP TIP files")
    if not os.path.exists(STCP_EXCEL_DF):
        df_stcp_excel = read_excel_files(STCP_EXCEL_PATH)
        df_stcp_excel.rename(columns={'Paragem' : 'stop_name'}, inplace=True)
        df_stcp_excel.to_csv(STCP_EXCEL_DF, index=False, header=True) #TODO: do after name matching with stops.txt? 
    else: 
        df_stcp_excel = pd.read_csv(STCP_EXCEL_DF)

    print("> Counting STCP Stop Validation")
    df_stcp_stop_count = count_vals_by_stop(df_stcp_excel)
    print("Number of lines in df_stcp_stop_count:", df_stcp_stop_count.shape[0])
    
    print("> Matching STCP stops with Centroids")
    df_centroids_stcp_vals = match_with_gtfs_stops(STCP_GTFS_STOPS, df_stcp_stop_count)

    print(" Number of zeros in stcp DF:" , len(df_centroids_stcp_vals[df_centroids_stcp_vals['validations'] != 0]))

    # merge metro and stcp summing the validations per section
    print("> Merging Metro and STCP")
    df_merged = pd.concat([df_centroids_metro_vals, df_centroids_stcp_vals]).groupby(['section_id']).sum().reset_index()
    df_merged['section_id'] = df_merged['section_id'].astype('int64')
    df_merged['validations'] = df_merged['validations'].astype('int64')

    avg_distance_to_node = pd.read_csv(AVG_DISTANCE_TO_NODE_CSV)
    avg_distance_to_node.rename(columns={'to': 'section_id'}, inplace=True)  

    final_output  = avg_distance_to_node.merge(df_merged, on='section_id', how='right')
    final_output['indicator'] = final_output['validations'] * final_output['weight']
    final_output.to_csv(RESULT_FILE, index=False, header=True)


if __name__ == "__main__":
    main()
