"""
Logging utilities for the Wilo scraper application
"""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional
from datetime import datetime

class CustomFormatter(logging.Formatter):
    """Custom formatter with colors for console output"""
    
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
        'RESET': '\033[0m'      # Reset
    }
    
    def format(self, record):
        if hasattr(record, 'no_color'):
            return super().format(record)
        
        color = self.COLORS.get(record.levelname, '')
        reset = self.COLORS['RESET']
        
        # Format with color
        record.levelname = f"{color}{record.levelname}{reset}"
        formatted = super().format(record)
        
        return formatted

class AppLogger:
    """Application logger manager"""
    
    def __init__(self, name: str = "wilo_scraper"):
        self.name = name
        self.logger = logging.getLogger(name)
        self.handlers = []
    
    def setup(self, log_config):
        """Setup logging configuration"""
        # Clear existing handlers
        self.logger.handlers.clear()
        
        # Set level
        level = getattr(logging, log_config.level.upper(), logging.INFO)
        self.logger.setLevel(level)
        
        # Create formatters
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s'
        )
        console_formatter = CustomFormatter(
            '%(asctime)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        self._setup_file_handler(log_config, file_formatter)
        
        # Console handler
        self._setup_console_handler(console_formatter)
        
        # Prevent propagation to root logger
        self.logger.propagate = False
    
    def _setup_file_handler(self, log_config, formatter):
        """Setup file logging handler"""
        try:
            # Ensure log directory exists
            log_file = Path(log_config.file)
            log_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Parse max file size
            max_bytes = self._parse_size(log_config.max_file_size)
            
            # Create rotating file handler
            file_handler = logging.handlers.RotatingFileHandler(
                log_config.file,
                maxBytes=max_bytes,
                backupCount=log_config.backup_count,
                encoding='utf-8'
            )
            file_handler.setFormatter(formatter)
            
            self.logger.addHandler(file_handler)
            self.handlers.append(file_handler)
            
        except Exception as e:
            print(f"Failed to setup file logging: {e}")
    
    def _setup_console_handler(self, formatter):
        """Setup console logging handler"""
        try:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            
            self.logger.addHandler(console_handler)
            self.handlers.append(console_handler)
            
        except Exception as e:
            print(f"Failed to setup console logging: {e}")
    
    def _parse_size(self, size_str: str) -> int:
        """Parse size string like '10MB' to bytes"""
        size_str = size_str.upper()
        
        if size_str.endswith('KB'):
            return int(size_str[:-2]) * 1024
        elif size_str.endswith('MB'):
            return int(size_str[:-2]) * 1024 * 1024
        elif size_str.endswith('GB'):
            return int(size_str[:-2]) * 1024 * 1024 * 1024
        else:
            return int(size_str)
    
    def get_logger(self):
        """Get the logger instance"""
        return self.logger

# Global logger instance
_app_logger = None

def setup_logging(log_config):
    """Setup application logging"""
    global _app_logger
    _app_logger = AppLogger()
    _app_logger.setup(log_config)

def get_logger(name: str = None):
    """Get logger instance"""
    if name:
        return logging.getLogger(name)
    
    if _app_logger:
        return _app_logger.get_logger()
    
    return logging.getLogger("wilo_scraper")

class LogCapture:
    """Capture logs for GUI display"""
    
    def __init__(self):
        self.logs = []
        self.max_logs = 1000
        
    def add_log(self, level: str, message: str, timestamp: Optional[datetime] = None):
        """Add a log entry"""
        if timestamp is None:
            timestamp = datetime.now()
        
        self.logs.append({
            'level': level,
            'message': message,
            'timestamp': timestamp
        })
        
        # Keep only the last max_logs entries
        if len(self.logs) > self.max_logs:
            self.logs = self.logs[-self.max_logs:]
    
    def get_logs(self, level: Optional[str] = None) -> list:
        """Get logs, optionally filtered by level"""
        if level is None:
            return self.logs.copy()
        
        return [log for log in self.logs if log['level'] == level]
    
    def clear(self):
        """Clear all logs"""
        self.logs.clear()
    
    def get_recent(self, count: int = 50) -> list:
        """Get recent logs"""
        return self.logs[-count:] if len(self.logs) > count else self.logs.copy()

class GUILogHandler(logging.Handler):
    """Custom log handler for GUI integration"""
    
    def __init__(self, log_capture: LogCapture):
        super().__init__()
        self.log_capture = log_capture
        
    def emit(self, record):
        """Emit a log record"""
        try:
            message = self.format(record)
            self.log_capture.add_log(record.levelname, message)
        except Exception:
            self.handleError(record)

# Example usage
if __name__ == "__main__":
    from config.settings import LogConfig
    
    # Test logging setup
    log_config = LogConfig()
    setup_logging(log_config)
    
    logger = get_logger()
    
    logger.debug("This is a debug message")
    logger.info("This is an info message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    logger.critical("This is a critical message")