#!/bin/bash
LOG_INTERVAL=600  # 10 minutes in seconds
while true; do
    /usr/bin/cpu_temp_monitor.py log
    sleep $LOG_INTERVAL
done