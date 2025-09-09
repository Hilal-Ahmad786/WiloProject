#!/bin/bash
echo "Starting Wilo Scraper..."
cd "$(dirname "$0")"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run the installer first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check if main file exists
if [ ! -f "wilo_scraper_gui.py" ]; then
    echo "Main application file not found. Please ensure all files are present."
    exit 1
fi

# Start the application
python wilo_scraper_gui.py
