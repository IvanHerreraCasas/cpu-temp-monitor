#!/bin/bash
# Source configuration file
source /etc/cpu-temp-monitor/config.ini

# Get logging interval from config or use default of 600 seconds
LOG_INTERVAL=${interval:-600}

# Function to get current time in nanoseconds
get_time_ns() {
    date +%s%N
}

# Function to perform temperature logging with precise timing
precise_monitor() {
    local interval_ns=$((LOG_INTERVAL * 1000000000))  # Convert seconds to nanoseconds
    local next_time=$(get_time_ns)
    
    while true; do
        current_time=$(get_time_ns)
        
        # Execute temperature logging
        cpu-temp-monitor log
        
        # Calculate next execution time
        next_time=$((next_time + interval_ns))
        
        # Calculate sleep time in seconds with nanosecond precision
        current_time=$(get_time_ns)
        sleep_ns=$((next_time - current_time))
        sleep_seconds=$(echo "scale=9; $sleep_ns / 1000000000" | bc)
        
        # If we've fallen behind schedule, reset next_time
        if (( sleep_ns < 0 )); then
            echo "Warning: Falling behind schedule, resetting timing" >&2
            next_time=$((current_time + interval_ns))
            sleep_seconds=0
        fi
        
        # Use proper sleep command based on duration
        if (( $(echo "$sleep_seconds >= 0.01" | bc -l) )); then
            sleep $sleep_seconds
        fi
    done
}

# Enhanced synchronization to wait for the start of a minute (second 00)
wait_for_minute_start() {
    current_seconds=$(date +%S)
    if [ "$current_seconds" != "00" ]; then
        # Calculate seconds until next minute
        seconds_to_wait=$((60 - current_seconds))
        
        # Wait until 0.1 seconds before the target time
        sleep $((seconds_to_wait - 1))
        
        # Fine-grained loop for the last second
        while [ "$(date +%S)" != "00" ]; do
            sleep 0.001
        done
    fi
}

echo "Synchronizing to start of next minute..."
wait_for_minute_start

echo "Starting CPU temperature monitoring at $(date +%Y-%m-%d\ %H:%M:%S.%N) with log interval: $LOG_INTERVAL"

# Start the monitoring
precise_monitor