import numpy as np
import pandas as pd
from glob import glob
import os
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import psutil

from atmosfunctions import *

high_res_folder_name = '/mnt/csl/datasets/ARS-NEPTUNE/BBDD/FINO1/10Hz/'
low_res_folder_name = '/mnt/csl/datasets/ARS-NEPTUNE/BBDD/FINO1/10min/2006/'

pickles_folder = '../../02Data/'


files = glob(low_res_folder_name + '**/*.dat', recursive=True)

df = pd.DataFrame()
for file in files[:]:
    parameter = file.split('_')[1]
    altitude = file.split('_')[2]
    if altitude[-1] != 'm':
        altitude = file.split('_')[3][:-1]
    else:
        altitude = file.split('_')[2][:-1]
    col_name = f'{parameter}_{altitude}'
    df_aux = pd.read_csv(file, sep='\t', skiprows=[0,1,2,3,5], encoding='latin1')
    df[col_name] = df_aux['Value']
df['datetime'] = df_aux['Time']
df['datetime'] = pd.to_datetime(df['datetime'])

if not os.path.exists('../02Data'):
    os.makedirs('../02Data')
    
df.to_pickle(pickles_folder + '10min_data')

df_min = pd.read_pickle(pickles_folder + '10min_data')

files = glob(high_res_folder_name + '**/*2006*.txt', recursive=True)

def read_file(file, df_min):
    """Read a single CSV file safely and ensure file closure."""
    try:
        if not file.endswith('.txt'):
            return None
        # Explicitly open file to guarantee closure
        with open(file, 'r') as f:
            df_file = pd.read_csv(f, sep=' ')
            df_file = df_file.reset_index(drop = True)
            df_file.columns = df_file.columns.str.replace('(', '_', regex=False)
            df_file.columns = df_file.columns.str.replace(')', '', regex=False)
            df_file['datetime_str'] = (df_file['Date'] + ' ' + df_file['Time']).str.replace(r':60(\.00)?', ':59', regex=True)
            df_file['datetime'] = pd.to_datetime(df_file['datetime_str'])
            df_file = df_file.drop(columns=['Date','Time'])
            df_file_processed = process_df_obukhov_length(df_min, df_file)
        return df_file_processed
    except Exception as e:
        print(f"[ERROR] Failed to read {file}: {e}")
        return None

# Prepare process handle for memory monitoring
process = psutil.Process(os.getpid())

# Read files in parallel
dfs = []
total_files = len(files)
print(f"Found {total_files} files. Starting parallel read...")

with ThreadPoolExecutor(max_workers=16) as executor:
    futures = {executor.submit(read_file, f, df_min): f for f in files}
    
    for i, future in enumerate(as_completed(futures), 1):
        file = futures[future]
        try:
            df_file = future.result()
            if df_file is not None:
                dfs.append(df_file)
                # Print completion and memory usage
                mem_MB = process.memory_info().rss / 1024**2
                print(f"[{i}/{total_files}] Completed: {file} "
                      f"(rows={len(df_file)}), memory={mem_MB:.2f} MB")
            else:
                mem_MB = process.memory_info().rss / 1024**2
                print(f"[{i}/{total_files}] Skipped: {file}, memory={mem_MB:.2f} MB")
        except Exception as e:
            mem_MB = process.memory_info().rss / 1024**2
            print(f"[{i}/{total_files}] Error processing {file}: {e}, memory={mem_MB:.2f} MB")

# Concatenate all DataFrames
df = pd.concat(dfs, ignore_index=True)

if not os.path.exists('../02Data'):
    os.makedirs('../02Data')

df = df.sort_values('datetime')    
df.to_pickle(pickles_folder + '10min_data_processed')

print(df.columns)