#!/bin/bash

# Source configuration file
source /etc/cpu-temp-monitor/config.ini

# Get logging interval from config or use default of 600 seconds
LOG_INTERVAL=${interval:-600}

# Function to calculate seconds until next minute
wait_for_zero_seconds() {
    # Get current seconds
    current_seconds=$(date +%S)
    
    if [ $current_seconds -eq 0 ]; then
        sleep 0.1  # Small delay to ensure we're past the zero second mark
    else
        # Calculate wait time until next minute
        wait_time=$((60 - current_seconds))
        echo "Waiting $wait_time seconds to synchronize with minute boundary..."
        sleep $wait_time
    fi
}

# Initial synchronization
echo "Synchronizing start time..."
wait_for_zero_seconds

echo "Starting CPU temperature monitoring at $(date) with log interval: $LOG_INTERVAL"

# Main monitoring loop
while true; do
    cpu-temp-monitor log
    sleep $LOG_INTERVAL
done
