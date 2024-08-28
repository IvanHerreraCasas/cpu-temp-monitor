#!/bin/bash
source /etc/cpu-temp-monitor/config.conf
LOG_INTERVAL=${Settings__log_interval:-600}
while true; do
    /usr/bin/cpu-temp-monitor log
    sleep $LOG_INTERVAL
done