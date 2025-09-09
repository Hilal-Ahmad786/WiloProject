#!/usr/bin/env python3
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
