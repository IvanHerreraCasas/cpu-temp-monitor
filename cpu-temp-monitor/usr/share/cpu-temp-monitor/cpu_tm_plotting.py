import ast
import socket
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

from cpu_tm_utils import open_file

def parse_temperatures(temp_str):
    temp_str = temp_str.split(': ', 1)[1]  # Remove "CPU Temperatures: " prefix
    return ast.literal_eval(temp_str)

def get_aggregation(type, data):
    if any(pd.isnull(data)):
        return np.nan
    if  type == 'mean':
            return np.mean(data)
    elif type == "max":
            return np.max(data)
    elif type == "min":
            return np.min(data)

def get_log_temperatures(args):
    log_file = args.input
    # Read the log file
    df = pd.read_csv(log_file, sep=" - ", header=None, names=['timestamp', 'temperatures'], engine='python')
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Parse the temperatures string into a dictionary
    df['temperatures'] = df['temperatures'].apply(parse_temperatures)

    # Explode the temperatures dictionary into separate columns
    temp_df = df['temperatures'].apply(pd.Series)
    df = pd.concat([df['timestamp'], temp_df], axis=1)
    
    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    return df

def filter_data(df, args):
    interval = args.interval
    start_time = args.start_time
    end_time = args.end_time

    time_index = pd.date_range(start=start_time, end=end_time, freq=f'{interval}s')
    df = df.reindex(time_index, tolerance=pd.Timedelta(seconds=interval), method="nearest")

    return df
        

def resample_data(df, args):
    days = args.days
    resolution = args.resolution
    type = args.type
    interval = args.interval

    # Resample data based on resolution
    if resolution == 'auto':
        if days <= 1:
            if 60 % interval == 0:
                resolution = 'minute'
            else:
                resolution = 'interval'
        elif days <= 35:
            resolution = 'hour'
        elif days <= 366:
            resolution = 'day'
        else:
            resolution = 'month'

    resample_map = {
        'interval': f'{interval}s',
        'minute': 'T',
        'hour': 'H',
        'day': 'D',
        'month': 'M'
    }
    
    df_resampled = df.resample(resample_map[resolution]).agg({col: lambda x: get_aggregation(type=type, data=x) for col in df.columns})
    
    if resolution == 'interval':
        if interval % 60 == 0:
            resolution = f'{interval // 60} minutes'
        else:
            resolution = f'{interval} seconds'
    return df_resampled, resolution

def save_plot(args):
    plot_filepath = str(args.filepath)

    plot_path = Path(plot_filepath)
    plot_path.parent.mkdir(exist_ok=True, parents=True)

    plt.savefig(plot_filepath, bbox_inches='tight')

    print(f"Plot saved as {plot_filepath}")

    return plot_filepath


def plot_temperatures(args):
    threshold = args.threshold
    cores = args.cores

    df = get_log_temperatures(args)
    df = filter_data(df, args)
 
    if df.empty:
        print(f"No data available for the specified time range")
        return

    df_resampled, resolution = resample_data(df, args)

    # Plot the data
    plt.figure(figsize=(12, 6))
    
    if cores[0].startswith("all"):
        if cores[0] == "all":
                for column in df_resampled.columns:
                    plt.plot(df_resampled.index, df_resampled[column], label=column)
        elif cores[0] == "all-mean":
                df_resampled['mean-temperature'] = df_resampled.mean(axis=1)
                plt.plot(df_resampled.index, df_resampled['mean-temperature'], label='Mean CPU Temperature')
        elif cores[0] == "all-max":
                df_resampled['max-temperature'] = df_resampled.max(axis=1)
                plt.plot(df_resampled.index, df_resampled['max-temperature'], label='Max CPU Temperature')
        elif cores[0] == "all-min":
                df_resampled['min-temperature'] = df_resampled.min(axis=1)
                plt.plot(df_resampled.index, df_resampled['min-temperature'], label='Min CPU Temperature')
    else:
        for core in cores:
            core_label = f"Core {core}"
            if core_label in df_resampled.columns:
                plt.plot(df_resampled.index, df_resampled[core_label], label=core_label)
            else:
                print(f"Warning: Core {core} not found in the data")

    hostname = socket.gethostname()
    plt.title(f"CPU Temperature of {hostname} ({resolution} resolution)")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.legend(loc='upper center', bbox_to_anchor=(0.5, -0.25), ncol=4)
    plt.tight_layout(pad=1.25)

    if args.show_threshold:
        plt.axhline(y=threshold, color='r', linestyle='-', label='Threshold')


    plt.gcf().autofmt_xdate()

    plot_filepath = save_plot(args)

    if args.show:
        open_file(plot_filepath)
