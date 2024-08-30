from pathlib import Path
import os
import configparser
from datetime import datetime, timedelta

from cpu_tm_utils import open_file
from cpu_tm_logging import log_temperatures
from cpu_tm_plotting import plot_temperature

class CPUTempMonitor:
    def __init__(self, config_file, cron_file):
        self.config_file = config_file
        self.cron_file = cron_file
        self.config = self._load_config()
        self.settings = self.config['Settings']
        self.cron = self.config['cron']

    def _load_config(self):
        config = configparser.ConfigParser()
        config.read(self.config_file)
        return config

    def _update_config(self):
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

    def _update_cron(self):
        cron_job = f"*/{self.log_interval} * * * * root cpu-temp-monitor log\n"
        
        with open(self.cron_file, 'w') as cron_file:
            cron_file.write(cron_job)

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
        return self.cron.getint('interval', 10)
    
    @property
    def def_threshold(self):
        return self.settings.getint('threshold', 80)
    

    def open_app_file(self, args):
        file = args.file
        match file:
            case "config":
                open_file(self.config_file)
            case "log":
                log_file = self.def_log_file
                open_file(log_file)
            case "plot":
                plot_dir = self.def_plot_dir
                plot_filename = self.def_plot_filename
                plot_filepath = Path(os.path.expanduser(plot_dir), plot_filename)
                open_file(plot_filepath)

    def log_temperatures(self, args):
        log_temperatures(args)

    def plot_temperature(self, args):
        args.interval = self.log_interval

        if args.filepath is None:
            args.filepath = Path(os.path.expanduser(self.def_plot_dir), args.filename)
        
        if args.range is not None:
            args.start_time = datetime.strptime(args.range[0], "%Y%m%d_%H%M%S")
            args.end_time = datetime.strptime(args.range[1], "%Y%m%d_%H%M%S")
        else:        
            args.start_time = datetime.now() - timedelta(days=args.days)
            args.end_time = datetime.now()

        plot_temperature(args)

    def set_interval(self, args):
        self.config['cron']['interval'] = str(args.interval)
        self._update_cron()
        self._update_config()
