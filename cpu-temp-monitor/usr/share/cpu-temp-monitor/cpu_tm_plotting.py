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
    match type:
        case 'mean':
            return np.mean(data)
        case 'max':
            return np.max(data)
        case 'min':
            return np.min(data)

def get_log_temperatures(args):
    log_file = args.log_file
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

    time_index = pd.date_range(start=start_time, end=end_time, freq=f'{interval}T')
    df = df.reindex(time_index, tolerance=pd.Timedelta(minutes=interval), method="nearest")

    return df
        

def resample_data(df, args):
    days = args.days
    resolution = args.resolution
    type = args.type
    interval = args.interval

    # Resample data based on resolution
    if resolution == 'auto':
        if days <= 1:
            resolution = 'interval'
        elif days <= 35:
            resolution = 'hour'
        elif days <= 366:
            resolution = 'day'
        else:
            resolution = 'month'

    resample_map = {
        'interval': f'{interval}T',
        'hour': 'H',
        'day': 'D',
        'month': 'M'
    }
    
    df_resampled = df.resample(resample_map[resolution]).agg({col: lambda x: get_aggregation(type=type, data=x) for col in df.columns})
    return df_resampled

def save_plot(args):
    plot_filepath = args.filepath

    plot_path = Path(plot_filepath)
    plot_path.parent.mkdir(exist_ok=True, parents=True)

    plt.savefig(plot_path)

    print(f"Plot saved as {plot_filepath}")

    return plot_filepath


def plot_temperature(args):
    days = args.days
    resolution = args.resolution
    threshold = args.threshold
    cores = args.cores

    df = get_log_temperatures(args)
    df = filter_data(df, args)
 
    if df.empty:
        print(f"No data available for the specified time range")
        return

    df_resampled = resample_data(df, args)

    # Plot the data
    plt.figure(figsize=(12, 6))
    
    if cores[0].startswith("all"):
        match cores[0]:
            case "all":
                for column in df_resampled.columns:
                    plt.plot(df_resampled.index, df_resampled[column], label=column)
            case "all-mean":
                df_resampled['mean-temperature'] = df_resampled.mean(axis=1)
                plt.plot(df_resampled.index, df_resampled['mean-temperature'], label='Mean CPU Temperature')
            case "all-max":
                df_resampled['max-temperature'] = df_resampled.max(axis=1)
                plt.plot(df_resampled.index, df_resampled['max-temperature'], label='Max CPU Temperature')
            case "all-min":
                df_resampled['min-temperature'] = df_resampled.min(axis=1)
                plt.plot(df_resampled.index, df_resampled['min-temperature'], label='Min CPU Temperature')
    else:
        for core in cores:
            if core in df_resampled.columns:
                plt.plot(df_resampled.index, df_resampled[core], label=core)
            else:
                print(f"Warning: Core {core} not found in the data")

    hostname = socket.gethostname()
    plt.title(f"CPU Temperature of {hostname} Over the Last {days} Days ({resolution} resolution)")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)
    plt.legend(loc='center left', bbox_to_anchor=(1, 0.5))
    plt.tight_layout(pad=1.25)

    if args.add_threshold:
        plt.axhline(y=threshold, color='r', linestyle='-', label='Threshold')

    # Format x-axis based on resolution
    if resolution in ['interval', 'hour']:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()

    plot_filepath = save_plot(args)

    if args.show:
        open_file(plot_filepath)