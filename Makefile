# Makefile for CPU Temperature Monitor

# Define variables
PREFIX ?= /usr/
DESTDIR ?=

# Directories
SHAREDIR = $(DESTDIR)$(PREFIX)/share/cpu-temp-monitor
ETCDIR = $(DESTDIR)/etc/cpu-temp-monitor

# Files
PYTHON_SCRIPT = cpu-temp-monitor/usr/share/cpu-temp-monitor/cpu-temp-monitor.py
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
	install -m 744 $(PYTHON_SCRIPT) $(SHAREDIR)/cpu-temp-monitor.py

	# Install config file
	install -m 644 $(CONFIG_FILE) $(ETCDIR)/config.ini

clean:
	@echo "Nothing to clean."