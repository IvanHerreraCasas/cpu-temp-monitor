import subprocess
from typing import Any, Optional

class CPUTempService:
    def __init__(self, name: str='cpu-temp-monitor.service') -> None:
        """
        Initialize the service with a given name.

        :param name: Name of the systemd service to manage
        """
        self.name = name

    def _run_systemctl_command(self, command: str) -> Optional[subprocess.CompletedProcess]:
        """
        Helper method to run systemctl commands.

        Does not raise on a non-zero exit code: several systemctl subcommands
        (notably ``status``) use the return code to report state rather than
        failure, so callers inspect ``returncode`` themselves.

        :param command: The systemctl subcommand to run
        :return: The CompletedProcess, or None if the command could not be run
        """
        try:
            return subprocess.run(
                ['sudo', 'systemctl', command, self.name],
                capture_output=True,
                text=True,
            )
        except OSError as e:
            print(f"Error running systemctl {command} for {self.name}: {e}")
            return None

    def _run_action(self, command: str, success_msg: str, failure_msg: str) -> bool:
        """Run a state-changing systemctl command and report the outcome."""
        result = self._run_systemctl_command(command)
        ok = result is not None and result.returncode == 0
        print(success_msg if ok else failure_msg)
        if result is not None and not ok and result.stderr.strip():
            print(result.stderr.strip())
        return ok

    def start(self, args: Any = None) -> bool:
        """
        Start the service.

        :param args: Optional argparse Namespace (can be None)
        :return: True if service started successfully, False otherwise
        """
        return self._run_action('start', f"Service {self.name} started.", "Failed to start service.")

    def stop(self, args: Any = None) -> bool:
        """
        Stop the service.

        :param args: Optional argparse Namespace (can be None)
        :return: True if service stopped successfully, False otherwise
        """
        return self._run_action('stop', f"Service {self.name} stopped.", "Failed to stop service.")

    def restart(self, args: Any = None) -> bool:
        """
        Restart the service.

        :param args: Optional argparse Namespace (can be None)
        :return: True if service restarted successfully, False otherwise
        """
        return self._run_action('restart', f"Service {self.name} restarted.", "Failed to restart service.")

    def status(self, args: Any = None) -> Optional[str]:
        """
        Get the status of the service.

        ``systemctl status`` exits non-zero when the unit is inactive (3) or
        not found (4) while still printing useful information, so the output is
        shown regardless of the return code.

        :param args: Optional argparse Namespace (can be None)
        :return: Service status output or None if the command could not be run
        """
        result = self._run_systemctl_command('status')
        if result is None:
            return None
        output = result.stdout.strip() or result.stderr.strip()
        if output:
            print(output)
        return output
    
    def enable(self, args: Any = None) -> bool:
        """
        Enable the service to start automatically on boot.
        
        :param args: Optional argparse Namespace (can be None)
        :return: True if service was enabled successfully, False otherwise
        """
        return self._run_action(
            'enable',
            f"Service {self.name} enabled to start on boot.",
            "Failed to enable service.",
        )

    def disable(self, args: Any = None) -> bool:
        """
        Disable the service from starting automatically on boot.

        :param args: Optional argparse Namespace (can be None)
        :return: True if service was disabled successfully, False otherwise
        """
        return self._run_action(
            'disable',
            f"Service {self.name} disabled from starting on boot.",
            "Failed to disable service.",
        )
