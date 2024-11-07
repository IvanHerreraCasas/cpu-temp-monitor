from pathlib import Path
import os
import configparser
from datetime import datetime, timedelta

from cpu_tm_utils import open_file, IntervalException
from cpu_tm_logging import log_temperatures
from cpu_tm_plotting import plot_temperatures
class CPUTempMonitor:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self._load_config()
        self.settings = self.config['Settings']

    def _load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        return config

    def _update_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    @property
    def def_log_file(self):
        return self.settings.get('log_file', '/var/log/cpu-temp-monitor/pc_temperature.log')
    
    @property
    def def_plot_dir(self):
        return self.settings.get('plot_dir', '~/.local/share/cpu-temp-monitor/')
    
    @property
    def def_plot_filename(self):
        return self.settings.get('plot_filename', 'cpu_temperature_plot.png')
    
    @property
    def log_interval(self):
        interval = self.settings.getint('interval', 600)
        if 3600 % interval != 0:
            raise IntervalException("Interval must be a divisor of 1 hour == 3600s")
        return interval
    
    @property
    def def_threshold(self):
        return self.settings.getint('threshold', 80)
    

    def open_app_file(self, args):
        file = args.file
        if file == "config":
                open_file(self.config_file)
        elif file == "log":
                log_file = self.def_log_file
                open_file(log_file)
        elif file == "plot":
                plot_dir = self.def_plot_dir
                plot_filename = self.def_plot_filename
                plot_filepath = Path(os.path.expanduser(plot_dir), plot_filename)
                open_file(plot_filepath)

    def log_temperatures(self, args):
        log_temperatures(args)

    def plot_temperatures(self, args):
        args.interval = self.log_interval

        if args.filepath is None:
            args.filepath = Path(os.path.expanduser(self.def_plot_dir), args.filename)
        
        if args.range is not None:
            args.start_time = datetime.strptime(args.range[0], "%Y%m%d_%H%M%S")
            args.end_time = datetime.strptime(args.range[1], "%Y%m%d_%H%M%S")
        else:        
            args.start_time = datetime.now() - timedelta(days=args.days)
            args.end_time = datetime.now()

        plot_temperatures(args)
