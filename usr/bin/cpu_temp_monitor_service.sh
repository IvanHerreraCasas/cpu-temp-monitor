#!/bin/bash
source /etc/cpu_temp_monitor/config.ini
LOG_INTERVAL=${Settings__log_interval:-600}
while true; do
    /usr/bin/cpu_temp_monitor.py log
    sleep $LOG_INTERVAL
done