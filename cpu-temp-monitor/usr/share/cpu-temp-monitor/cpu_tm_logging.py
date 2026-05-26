import ast
import subprocess
import csv
import re
from pathlib import Path
from datetime import datetime


def get_temperatures():
    try:
        output = subprocess.check_output(["sensors"]).decode()
        temperatures = {}
        for line in output.split("\n"):
            if line.startswith("Core "):
                core = line.split(":")[0].strip()
                temp = float(line.split("+")[1].split("°")[0])
                temperatures[core] = str(temp)
        return temperatures
    except Exception as e:
        print(f"Error getting temperatures: {e}")
    return None

def log_temperatures(args):
    log_file = args.file
    log_path = Path(log_file)
    log_path.parent.mkdir(exist_ok=True, parents=True)

    temps = get_temperatures()
    if temps:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check if file exists
        if log_path.exists():
            # Read the first line to determine format
            with log_path.open('r') as f:
                first_line = f.readline().strip()
            
            # Check if it's in the old format
            if re.match(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2} - CPU Temperatures:', first_line):
                # Convert old format to new CSV
                print("Converting log file to CSV format...")
                
                # Read all existing entries
                entries = []
                with log_path.open('r') as f:
                    for line in f:
                        # Extract timestamp and temperatures
                        match = re.match(r'([\d-]+ [\d:]+) - CPU Temperatures: ({.*})', line.strip())
                        if match:
                            entry_ts = match.group(1)
                            temps_dict = ast.literal_eval(match.group(2))  # Convert string representation to dict
                            entries.append((entry_ts, temps_dict))

                # Create new CSV file
                temp_log_path = log_path.with_suffix('.csv')
                with temp_log_path.open('w', newline='') as f:
                    # Determine all unique cores, preserving first-seen order so
                    # the header is deterministic and data rows stay aligned.
                    all_cores = []
                    for _, temp_dict in entries:
                        for core in temp_dict:
                            if core not in all_cores:
                                all_cores.append(core)

                    # Write headers
                    headers = ['Timestamp'] + all_cores
                    writer = csv.writer(f)
                    writer.writerow(headers)
                    
                    # Write data rows
                    for entry_ts, temp_dict in entries:
                        row = [entry_ts] + [temp_dict.get(core, '') for core in headers[1:]]
                        writer.writerow(row)
                
                # Remove old log file and rename new file
                log_path.unlink()
                temp_log_path.rename(log_path)
                print("Log file converted successfully.")
            
            # If the file already has content, follow its existing header so
            # appended rows stay aligned with the columns. Otherwise (re)create
            # the header from the current reading.
            has_content = log_path.stat().st_size > 0
            if has_content:
                with log_path.open("r", newline='') as f:
                    header = next(csv.reader(f), None)
                cores = header[1:] if header else list(temps.keys())
            else:
                cores = list(temps.keys())

            with log_path.open("a", newline='') as f:
                writer = csv.writer(f)
                if not has_content:
                    writer.writerow(['Timestamp'] + cores)
                writer.writerow([timestamp] + [temps.get(core, '') for core in cores])
        else:
            # New file, create with headers
            with log_path.open("w", newline='') as f:
                writer = csv.writer(f)
                headers = ['Timestamp'] + list(temps.keys())
                writer.writerow(headers)
                row = [timestamp] + [temps.get(core, '') for core in temps.keys()]
                writer.writerow(row)
        
        print(f"Logged temperatures: {temps}")
    else:
        print("Failed to get temperatures")