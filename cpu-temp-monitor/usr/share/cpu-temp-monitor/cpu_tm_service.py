import subprocess
from typing import Any, Optional

class CPUTempService:
    def __init__(self, name: str='cpu-temp-monitor.service') -> None:
        """
        Initialize the service with a given name.
        
        :param name: Name of the systemd service to manage
        """
        self.name = name
    
    def _run_systemctl_command(self, command: str) -> Optional[str]:
        """
        Helper method to run systemctl commands.
        
        :param command: The systemctl subcommand to run
        :return: Output of the command if successful, None otherwise
        """
        try:
            result = subprocess.run(
                ['sudo', 'systemctl', command, self.name], 
                capture_output=True, 
                text=True, 
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            print(f"Error running systemctl {command} for {self.name}: {e.stderr}")
            return None
        
    def start(self, args: Any = None) -> bool:
        """
        Start the service.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service started successfully, False otherwise
        """
        result = self._run_systemctl_command('start')
        print(f"Service {self.name} started." if result is not None else "Failed to start service.")
        return result is not None
    
    def stop(self, args: Any = None) -> bool:
        """
        Stop the service.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service stopped successfully, False otherwise
        """
        result = self._run_systemctl_command('stop')
        print(f"Service {self.name} stopped." if result is not None else "Failed to stop service.")
        return result is not None
    
    def restart(self, args: Any = None) -> bool:
        """
        Restart the service.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service restarted successfully, False otherwise
        """
        result = self._run_systemctl_command('restart')
        print(f"Service {self.name} restarted." if result is not None else "Failed to restart service.")
        return result is not None
    
    def status(self, args: Any = None) -> Optional[str]:
        """
        Get the status of the service.
        
        :param args: Optional argparse Namespace (can be None)
        :return: Service status output or None if failed
        """
        status_output = self._run_systemctl_command('status')
        if status_output:
            print(status_output)
        return status_output
    
    def enable(self, args: Any = None) -> bool:
        """
        Enable the service to start automatically on boot.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service was enabled successfully, False otherwise
        """
        result = self._run_systemctl_command('enable')
        print(f"Service {self.name} enabled to start on boot." if result is not None else "Failed to enable service.")
        return result is not None
    
    def disable(self, args: Any = None) -> bool:
        """
        Disable the service from starting automatically on boot.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service was disabled successfully, False otherwise
        """
        result = self._run_systemctl_command('disable')
        print(f"Service {self.name} disabled from starting on boot." if result is not None else "Failed to disable service.")
        return result is not None
