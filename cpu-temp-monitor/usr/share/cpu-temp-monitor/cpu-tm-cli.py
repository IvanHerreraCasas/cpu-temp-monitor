#!/usr/bin/env python3

import argparse

from cpu_tm_monitor import CPUTempMonitor


def main():

    CONFIG_FILE = "/etc/cpu-temp-monitor/config.ini"
    
    monitor = CPUTempMonitor(CONFIG_FILE)

    parser = argparse.ArgumentParser(description="CPU Temperature Monitor CLI")
    subparsers = parser.add_subparsers(title="Subcommands", dest="subcommand")

    log_parser = subparsers.add_parser("log", help="Log CPU Temperature.")
    log_parser.add_argument("-f", "--file", help=f"Log file path (default: {monitor.def_log_file})", default=monitor.def_log_file)
    log_parser.set_defaults(func=monitor.log_temperatures)

    plot_parser = subparsers.add_parser("plot", help="Plot CPU Temperature")
    plot_parser.add_argument("-d", "--days", type=int, help=f"Last X days to be plotted. (default 7)", default=7)
    plot_parser.add_argument("--range", nargs=2, metavar=('START', 'END'), help="Date range to be plotted (YYYYMMDD_HHMMSS YYYYMMDD_HHMMSS). This options ignores --days parameter")
    plot_parser.add_argument("-fp", "--filepath", help=f"Filepath for the plot")
    plot_parser.add_argument("-fn", "--filename", help=f"Filename for the plot - saved in def dir (default: {monitor.def_plot_filename})", default=monitor.def_plot_filename)
    plot_parser.add_argument("-i", "--input", default=monitor.def_log_file, help=f"Input log file (default: {monitor.def_log_file})")
    plot_parser.add_argument("-r", "--resolution", choices=['interval', 'minute', 'hour', 'day', 'month', 'auto'], default='auto', help="Time resolution for the plot")
    plot_parser.add_argument("-t", "--type", choices=['mean', 'max', 'min'], default='mean', help="Type of aggregation for the plot")
    plot_parser.add_argument("-th", "--threshold", type=int, default=monitor.def_threshold, help="Threshold for the plot")
    plot_parser.add_argument("-show-th", "--show-threshold", action="store_true", help="Show threshold line on plot")
    plot_parser.add_argument("--show", action="store_true", help="Show the plot after saving")
    plot_parser.add_argument("-c", "--cores", nargs='+', default=['all-mean'], help="Specify cores to plot (e.g., 0, 1, 2, ...), 'all', 'all-mean', 'all-min', 'all-max' for all cores")
    plot_parser.set_defaults(func=monitor.plot_temperatures)

    open_parser = subparsers.add_parser("open", help="Open application-related files")
    open_parser.add_argument("file", choices=["config", "log", "plot"], help="File to open")
    open_parser.set_defaults(func=monitor.open_app_file)

    args = parser.parse_args()

    if args.subcommand is None:
        parser.print_help()
    else:
        args.func(args)


if __name__ == "__main__":
    main()