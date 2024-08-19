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

from pathlib import Path

CONFIG_FILE = "/etc/cpu_temp_monitor/config.ini"

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE)
    return config['Settings']

settings = load_config()

DEF_LOG_FILE = settings.get('log_file', '/var/log/cpu_temp_monitor/pc_temperature.log')
DEF_PLOT_FILE = settings.get('plot_file', '/var/log/cpu_temp_monitor/temperature_plot.png')
LOG_INTERVAL = int(settings.get('log_interval', 600))
DEF_THRESHOLD = int(settings.get('threshold', 80))
DEF_NO_THRESHOLD = bool(settings.get('no_threshold', False))

def get_temperature():
    try:
        output = subprocess.check_output(["sensors"]).decode()
        for line in output.split("\n"):
            if "Core 0" in line:
                return float(line.split("+")[1].split("°")[0])
    except Exception as e:
        print(f"Error getting temperature: {e}")
    return None

def log_temperature(args):
    log_file = args.file

    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True, parents=True),


    temp = get_temperature()
    os.mkdir
    if temp is not None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with log_path.open("a+") as f:
            f.write(f"{timestamp} - CPU Temperature: {temp}°C\n")
        print(f"Logged temperature: {temp}°C")
    else:
        print("Failed to get temperature")

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

def plot_temperature(args):
    days= int(args.days)
    plot_file = args.file
    log_file = args.log_file
    resolution = args.resolution
    type= args.type
    threshold = args.threshold

    with open(log_file, "r") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        parts = line.split(" - ")
        timestamp = datetime.datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        temp = float(parts[1].split(":")[1].strip()[:-2])
        data.append((timestamp, temp))

    df = pd.read_csv(log_file, sep=" - ", header=None, names=['timestamp', 'temperature'], engine='python')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['temperature'] = df['temperature'].str.extract(r'(\d+\.?\d*)').astype(float)


    # Set timestamp as index
    df.set_index('timestamp', inplace=True)

    # Filter data for the specified number of days
    start_time = datetime.datetime.now() - datetime.timedelta(days=days)
    end_time = datetime.datetime.now()
    time_index = pd.date_range(start=start_time, end=end_time, freq=f'{LOG_INTERVAL}s')
    df = df.reindex(time_index, tolerance=pd.Timedelta(seconds=LOG_INTERVAL), method="nearest")
 
    if df.empty:
        print(f"No data available for the last {days} days")
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
    df_resampled = df.resample(resample_map[resolution]).agg({'temperature': lambda x: get_aggregation(type=type, data=x)})

    # Plot the data
    plt.figure(figsize=(12, 6))
    plt.plot(df_resampled.index, df_resampled['temperature'])

    hostname = socket.gethostname()
    plt.title(f"CPU Temperature of {hostname} Over the Last {days} Days ({resolution} resolution)")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)

    plt.axhline(y = threshold, color = 'r', linestyle = '-')

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
    start_parser.set_defaults(func=log_temperature)

    plot_parser = subparsers.add_parser("plot", help="Plot CPU Temperature")
    plot_parser.add_argument("-d", "--days", help=f"Last X days to be plotted. (default 7)", default=7)
    plot_parser.add_argument("-f", "--file", help=f"Plot file (default: {DEF_PLOT_FILE})", default=DEF_PLOT_FILE)
    plot_parser.add_argument("-l", "--log_file", default=DEF_LOG_FILE, help=f"Input log file (default: {DEF_LOG_FILE})")
    plot_parser.add_argument("-r", "--resolution", choices=['interval', 'hour', 'day', 'month', 'auto'], default='auto', help="Time resolution for the plot")
    plot_parser.add_argument("-t", "--type", choices=['mean', 'max', 'min'], default='mean', help="Type of aggregation for the plot")
    plot_parser.add_argument("-th", "--threshold", default=DEF_THRESHOLD, help="Threshold for the plot")
    plot_parser.add_argument("-no-th", "--no-threshold", action="store_true", default=DEF_NO_THRESHOLD, help="No add threshold indicator")
    plot_parser.add_argument("--show", action="store_true", help="Show the plot after saving")
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