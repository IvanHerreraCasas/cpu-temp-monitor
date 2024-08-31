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
**Note:** The binary includes a cron job that logs the temperature periodically at an interval and to a file specified in the configuration file.

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

To modify the cron log interval:
```
sudo cpu-temp-monitor cron -i <interval>
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