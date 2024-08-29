import subprocess

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
                temperatures[core] = temp
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
        with log_path.open("a+") as f:
            f.write(f"{timestamp} - CPU Temperatures: {temps}\n")
        print(f"Logged temperatures: {temps}")
    else:
        print("Failed to get temperatures")