# Makefile for CPU Temperature Monitor

# Define variables
PREFIX ?= /usr/
DESTDIR ?=

# Directories
SHAREDIR = $(DESTDIR)$(PREFIX)/share/cpu-temp-monitor
ETCDIR = $(DESTDIR)/etc/cpu-temp-monitor

# Files
PYTHON_CLI_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu-tm-cli.py
PYTHON_MONITOR_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_monitor.py
PYTHON_LOGGING_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_logging.py
PYTHON_PLOTTING_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_plotting.py
PYTHON_UTILS_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_utils.py
CONFIG_FILE = cpu-temp-monitor/etc/cpu-temp-monitor/config.ini

# Targets
.PHONY: all install clean

all:
	@echo "Nothing to compile. Use 'make install' to install the package."

install:
	# Create directories
	install -d $(SHAREDIR)
	install -d $(ETCDIR)


	# Install Python script
	install -m 744 $(PYTHON_CLI_SCRIPT) $(SHAREDIR)/cpu-tm-cli.py
	install -m 444 $(PYTHON_MONITOR_SCRIPT) $(SHAREDIR)/cpu_tm_monitor.py
	install -m 444 $(PYTHON_LOGGING_SCRIPT) $(SHAREDIR)/cpu_tm_logging.py
	install -m 444 $(PYTHON_PLOTTING_SCRIPT) $(SHAREDIR)/cpu_tm_plotting.py
	install -m 444 $(PYTHON_UTILS_SCRIPT) $(SHAREDIR)/cpu_tm_utils.py

	# Install config file
	install -m 644 $(CONFIG_FILE) $(ETCDIR)/config.ini

clean:
	@echo "Nothing to clean."