"""
Enhanced logging utilities with GUI support
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from collections import deque
import threading

def setup_logging(log_level=logging.INFO):
    """Setup application logging"""
    
    # Handle log_level parameter properly
    if hasattr(log_level, 'level'):
        # If it's a LogConfig object, extract the level
        level_str = log_level.level
    elif isinstance(log_level, str):
        level_str = log_level
    else:
        level_str = 'INFO'
    
    # Convert string level to logging constant
    numeric_level = getattr(logging, level_str.upper(), logging.INFO)
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f'wilo_scraper_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create application logger
    logger = logging.getLogger('wilo_scraper')
    logger.info(f"Logging initialized - {log_file}")
    
    return logger

def get_logger(name):
    """Get logger for specific module"""
    return logging.getLogger(f'wilo_scraper.{name}')

class LogCapture:
    """Captures log messages for GUI display"""
    
    def __init__(self, max_entries=1000):
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.lock = threading.Lock()
    
    def add_entry(self, message, level='INFO'):
        """Add a log entry"""
        with self.lock:
            entry = {
                'timestamp': datetime.now(),
                'level': level,
                'message': message
            }
            self.entries.append(entry)
    
    def get_recent(self, count=50):
        """Get recent log entries"""
        with self.lock:
            return list(self.entries)[-count:]
    
    def clear(self):
        """Clear all entries"""
        with self.lock:
            self.entries.clear()

class GUILogHandler(logging.Handler):
    """Custom log handler for GUI display"""
    
    def __init__(self, log_capture):
        super().__init__()
        self.log_capture = log_capture
        
    def emit(self, record):
        """Emit a log record"""
        try:
            message = self.format(record)
            self.log_capture.add_entry(message, record.levelname)
        except Exception:
            pass  # Ignore errors in logging
