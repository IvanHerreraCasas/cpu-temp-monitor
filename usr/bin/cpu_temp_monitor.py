#!/usr/bin/env python3

import argparse
import configparser
import subprocess
import matplotlib.pyplot as plt
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

def openImage(path):
    imageViewerFromCommandLine = {'linux':'xdg-open',
                                  'win32':'explorer',
                                  'darwin':'open'}[sys.platform]
    subprocess.run([imageViewerFromCommandLine, path])

def plot_temperature(args):
    days= int(args.days)
    plot_file = args.file
    log_file = args.log_file

    with open(log_file, "r") as f:
        lines = f.readlines()

    data = []
    for line in lines:
        parts = line.split(" - ")
        timestamp = datetime.datetime.strptime(parts[0], "%Y-%m-%d %H:%M:%S")
        temp = float(parts[1].split(":")[1].strip()[:-2])
        data.append((timestamp, temp))

    cutoff = datetime.datetime.now() - datetime.timedelta(days=days)
    recent_data = [(t, temp) for t, temp in data if t > cutoff]
    
    if not recent_data:
        print(f"No data available for the last {days} days")
        return

    timestamps, temperatures = zip(*recent_data)

    plt.figure(figsize=(12, 6))
    plt.plot(timestamps, temperatures)
    
    hostname = socket.gethostname()
    plt.title(f"CPU Temperature of {hostname} Over the Last {days} Days")
    plt.xlabel("Date")
    plt.ylabel("Temperature (°C)")
    plt.grid(True)

    plt.gca().xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
    plt.gcf().autofmt_xdate()

    plt.savefig(plot_file)
    print(f"Plot saved as {plot_file}")

    if args.show:
        openImage(plot_file)


def main():
    parser = argparse.ArgumentParser(description="CPU Temperature Monitor CLI")

    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    start_parser = subparsers.add_parser("log", help="Start logging CPU Temperature.")
    start_parser.add_argument("-f", "--file", help=f"Log file (default: {DEF_LOG_FILE})", default=DEF_LOG_FILE)
    start_parser.set_defaults(func=log_temperature)

    plot_parser = subparsers.add_parser("plot", help="Plot CPU Temperature")
    plot_parser.add_argument("-d", "--days", help=f"Last X days to be plotted. (default 7)", default=7)
    plot_parser.add_argument("-f", "--file", help=f"Plot file (default: {DEF_PLOT_FILE})", default=DEF_PLOT_FILE)
    plot_parser.add_argument("-l", "--log_file", default=DEF_LOG_FILE, help=f"Input log file (default: {DEF_LOG_FILE})")
    plot_parser.add_argument("--show", action="store_true", help="Show the plot after saving")
    plot_parser.set_defaults(func=plot_temperature)

    args = parser.parse_args()
    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()