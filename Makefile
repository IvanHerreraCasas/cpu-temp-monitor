# Makefile for CPU Temperature Monitor

# Define variables
PREFIX ?= /usr
DESTDIR ?=

# Directories
SHAREDIR = $(DESTDIR)$(PREFIX)/share/cpu-temp-monitor
ETCDIR = $(DESTDIR)/etc/cpu-temp-monitor
BINDIR = $(DESTDIR)$(PREFIX)/bin

# Files
PYTHON_CLI_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu-tm-cli.py
PYTHON_MONITOR_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_monitor.py
PYTHON_LOGGING_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_logging.py
PYTHON_PLOTTING_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_plotting.py
PYTHON_UTILS_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_utils.py
PYTHON_SERVICE_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu_tm_service.py

CONFIG_FILE = cpu-temp-monitor/etc/cpu-temp-monitor/config.ini
SH_SERVICE_FILE = cpu-temp-monitor/usr/bin/cpu-tm-service.sh

# Targets
.PHONY: all install clean

all:
	@echo "Nothing to compile. Use 'make install' to install the package."

install:
	# Create directories
	install -d $(SHAREDIR)
	install -d $(ETCDIR)
	install -d $(BINDIR)


	# Install Python script
	install -m 744 $(PYTHON_CLI_SCRIPT) $(SHAREDIR)/cpu-tm-cli.py
	install -m 444 $(PYTHON_MONITOR_SCRIPT) $(SHAREDIR)/cpu_tm_monitor.py
	install -m 444 $(PYTHON_LOGGING_SCRIPT) $(SHAREDIR)/cpu_tm_logging.py
	install -m 444 $(PYTHON_PLOTTING_SCRIPT) $(SHAREDIR)/cpu_tm_plotting.py
	install -m 444 $(PYTHON_UTILS_SCRIPT) $(SHAREDIR)/cpu_tm_utils.py
	install -m 444 $(PYTHON_SERVICE_SCRIPT) $(SHAREDIR)/cpu_tm_service.py

	# Install config file
	install -m 644 $(CONFIG_FILE) $(ETCDIR)/config.ini

	# Install SH service script
	install -m 744 $(SH_SERVICE_FILE) $(BINDIR)/cpu-tm-service.sh

clean:
	@echo "Nothing to clean."