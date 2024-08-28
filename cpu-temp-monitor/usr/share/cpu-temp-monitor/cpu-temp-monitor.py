#!/usr/bin/env python3

import argparse
import configparser
import subprocess
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import datetime
import matplotlib.dates as mdates
import socket
import os
import sys
import subprocess
import ast

from pathlib import Path

CONFIG_FILE = "/etc/cpu-temp-monitor/config.conf"

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['Settings']

settings = load_config()

DEF_LOG_FILE = settings.get('log_file', '/var/log/cpu-temp-monitor/pc_temperature.log')
DEF_PLOT_FILE = settings.get('plot_file', '/var/log/cpu-temp-monitor/temperature_plot.png')
LOG_INTERVAL = int(settings.get('log_interval', 600))
DEF_THRESHOLD = int(settings.get('threshold', 80))
DEF_NO_THRESHOLD = bool(settings.get('no_threshold', False))

def get_temperatures():
    try:
        output = subprocess.check_output(["sensors"]).decode()
        temperatures = {}
        for line in output.split("\n"):
            if line.startswith("Core "):
                core = line.split(":")[0].strip()
                temp = float(line.split("+")[1].split("°")[0])
                temperatures[core] = temp
        return temperatures
    except Exception as e:
        print(f"Error getting temperatures: {e}")
    return None

def log_temperatures(args):
    log_file = args.file
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True, parents=True)

    temps = get_temperatures()
    if temps:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a+") as f:
            f.write(f"{timestamp} - CPU Temperatures: {temps}\n")
        print(f"Logged temperatures: {temps}")
    else:
        print("Failed to get temperatures")


def open_file(file_path):
    os.system(f"xdg-open {file_path}")

def open_app_file(file):
    match file:
        case "config":
            open_file(CONFIG_FILE)
        case "log":
            open_file(DEF_LOG_FILE)
        case "plot":
            open_file(DEF_PLOT_FILE)

def openImage(path):
    imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
    subprocess.run([imageViewerFromCommandLine, path])

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
        
def parse_temperatures(temp_str):
    temp_str = temp_str.split(': ', 1)[1]  # Remove "CPU Temperatures: " prefix
    return ast.literal_eval(temp_str)

def plot_temperature(args):
    days = int(args.days)
    date_range = args.range
    plot_file = args.file
    log_file = args.log_file
    resolution = args.resolution
    type = args.type
    threshold = args.threshold
    cores = args.cores

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

    if date_range is not None:
        start_time = datetime.datetime.strptime(date_range[0], "%Y%m%d_%H%M%S")
        end_time = datetime.datetime.strptime(date_range[1], "%Y%m%d_%H%M%S")
    else:        
        start_time = datetime.datetime.now() - datetime.timedelta(days=days)
        end_time = datetime.datetime.now()

    time_index = pd.date_range(start=start_time, end=end_time, freq=f'{LOG_INTERVAL}s')
    df = df.reindex(time_index, tolerance=pd.Timedelta(seconds=LOG_INTERVAL), method="nearest")
 
    if df.empty:
        print(f"No data available for the specified time range")
        return

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
        'interval': f'{LOG_INTERVAL}s',
        'hour': 'H',
        'day': 'D',
        'month': 'M'
    }
    
    df_resampled = df.resample(resample_map[resolution]).agg({col: lambda x: get_aggregation(type=type, data=x) for col in df.columns})

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

    if not args.no_threshold:
        plt.axhline(y=threshold, color='r', linestyle='-', label='Threshold')

    # Format x-axis based on resolution
    if resolution in ['interval', 'hour']:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d %H:%M"))
    else:
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()

    plt.savefig(plot_file)
    print(f"Plot saved as {plot_file}")

    if args.show:
        openImage(plot_file)


def main():
    parser = argparse.ArgumentParser(description="CPU Temperature Monitor CLI")

    parser.add_argument("--open", choices=["config", "log", "plot"], help="Open app related files.")

    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    start_parser = subparsers.add_parser("log", help="Start logging CPU Temperature.")
    start_parser.add_argument("-f", "--file", help=f"Log file (default: {DEF_LOG_FILE})", default=DEF_LOG_FILE)
    start_parser.set_defaults(func=log_temperatures)

    plot_parser = subparsers.add_parser("plot", help="Plot CPU Temperature")
    plot_parser.add_argument("-d", "--days", help=f"Last X days to be plotted. (default 7)", default=7)
    plot_parser.add_argument("--range", nargs=2, help="Date range to be plotted (YYYYMMDD_HHMMSS YYYYMMDD_HHMMSS). This options ignores --days parameter")
    plot_parser.add_argument("-f", "--file", help=f"Plot file (default: {DEF_PLOT_FILE})", default=DEF_PLOT_FILE)
    plot_parser.add_argument("-l", "--log_file", default=DEF_LOG_FILE, help=f"Input log file (default: {DEF_LOG_FILE})")
    plot_parser.add_argument("-r", "--resolution", choices=['interval', 'hour', 'day', 'month', 'auto'], default='auto', help="Time resolution for the plot")
    plot_parser.add_argument("-t", "--type", choices=['mean', 'max', 'min'], default='mean', help="Type of aggregation for the plot")
    plot_parser.add_argument("-th", "--threshold", default=DEF_THRESHOLD, help="Threshold for the plot")
    plot_parser.add_argument("-no-th", "--no-threshold", action="store_true", default=DEF_NO_THRESHOLD, help="No add threshold indicator")
    plot_parser.add_argument("--show", action="store_true", help="Show the plot after saving")
    plot_parser.add_argument("-c", "--cores", nargs='+', default=['all-mean'], help="Specify cores to plot (e.g., 'Core 0 Core 1'), 'all', 'all-mean', 'all-min', 'all-max' for all cores")
    plot_parser.set_defaults(func=plot_temperature)

    args = parser.parse_args()

    if args.open is not None:
        open_app_file(args.open)
    elif args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()