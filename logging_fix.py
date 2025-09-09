#!/usr/bin/env python3
"""
Fix logging setup issue
"""

def fix_logger_setup():
    """Fix the logger setup function"""
    
    logger_content = '''"""
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
'''
    
    with open('utils/logger.py', 'w') as f:
        f.write(logger_content)
    
    print("✅ Fixed utils/logger.py - properly handles log level parameter")

def fix_main_py():
    """Fix main.py to handle settings properly"""
    
    main_content = '''#!/usr/bin/env python3
"""
Wilo Product Scraper - Main Entry Point
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    """Main application entry point"""
    try:
        from config.settings import AppSettings
        from utils.logger import setup_logging, get_logger
        from gui.main_window import MainWindow
        
        # Load settings first
        settings = AppSettings()
        
        # Setup logging with proper level
        setup_logging()  # Use default INFO level
        logger = get_logger(__name__)
        
        logger.info("Starting Wilo Scraper Application")
        
        # Create GUI
        root = tk.Tk()
        app = MainWindow(root, settings)
        
        # Start application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    with open('main.py', 'w') as f:
        f.write(main_content)
    
    print("✅ Fixed main.py - proper initialization order")

def main():
    """Main fix function"""
    print("🔧 Fixing Logging Setup Issues")
    print("=" * 40)
    
    # Fix logger setup
    fix_logger_setup()
    
    # Fix main.py
    fix_main_py()
    
    print("\n✅ Logging issues fixed!")
    print("\n🎯 Try running the application:")
    print("python main.py")

if __name__ == "__main__":
    main()