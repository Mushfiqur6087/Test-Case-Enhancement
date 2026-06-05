"""Simplified debug logging for the Test Case Enhancement."""

from datetime import datetime
from pathlib import Path


class DebugLogger:
    """Debug logging utility for consistent log file management."""

    def __init__(self):
        self.logs_dir = Path(__file__).resolve().parent.parent / "logs"
        self.logs_dir.mkdir(exist_ok=True)

    def get_debug_file_path(self, component: str, debug_file_prefix: str = None) -> str:
        """Generate a debug file path in the logs directory."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        if debug_file_prefix:
            filename = f"{debug_file_prefix}_{component}_{timestamp}.log"
        else:
            filename = f"{component}_debug_{timestamp}.log"
        return str(self.logs_dir / filename)

    def get_logs_directory(self) -> Path:
        """Get the logs directory path."""
        return self.logs_dir
