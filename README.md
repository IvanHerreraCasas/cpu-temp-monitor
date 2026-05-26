# cpu-temp-monitor

`cpu-temp-monitor` is a command-line tool to log CPU core temperatures and plot them.

## Installation

Download the Debian binary and install it using:
```
sudo apt install <binary>
```
Or create one from the source tarball.

## Usage

### Logging Temperatures

To log the core temperatures:
```
cpu-temp-monitor log [-f FILE]
```
**Note:** The package installs a systemd service (`cpu-temp-monitor.service`) that
logs the temperature periodically. The logging interval and log file are taken
from the configuration file. The service is enabled and started automatically on
installation.

### Controlling the Service

Manage the background logging service:
```
cpu-temp-monitor start      # start logging now
cpu-temp-monitor stop       # stop logging
cpu-temp-monitor restart    # restart (e.g. after changing the interval)
cpu-temp-monitor status     # show the service status
cpu-temp-monitor enable     # start automatically on boot
cpu-temp-monitor disable    # do not start on boot
```
These commands wrap `systemctl` and use `sudo`, so you may be prompted for your
password.

### Plotting Temperatures

To plot the logged temperatures:
```
cpu-temp-monitor plot [-d DAYS] [--range START END] [-fp FILEPATH] [-fn FILENAME] 
                      [-i INPUT] [-r {interval,hour,day,month,auto}] 
                      [-t {mean,max,min}] [-c CORES [CORES ...]] 
                      [-th THRESHOLD] [-show-th] [--show]
```

### Opening Files

To open the log, plot, or config files:
```
cpu-temp-monitor open {log,plot,config}
```

### Configuration

The configuration file (located at `/etc/cpu-temp-monitor/config.ini`) includes defaults for:
- log_file
- plot_dir
- plot_filename
- threshold
- interval (logging interval in seconds, used by the service)

To change the logging interval, edit the `interval` value in the configuration
file and restart the service:
```
sudo cpu-temp-monitor restart
```

## Dependencies

- lm-sensors
- python3 (>=3.6)
- python3-pandas
- python3-numpy
- python3-matplotlib

## Options

For detailed information on available options, use:
```
cpu-temp-monitor --help
```
or
```
cpu-temp-monitor <subcommand> --help
```