"""
Main scraper tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from config.countries import get_all_countries, COUNTRIES
from utils.logger import get_logger

class ScraperTab:
    """Main scraper tab"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.logger = get_logger(__name__)
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
    def create_widgets(self):
        """Create tab widgets"""
        
        # Country selection
        country_frame = ttk.LabelFrame(self.frame, text="Country Selection", padding=10)
        country_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(country_frame, text="Select Country:").pack(anchor=tk.W)
        
        self.country_var = tk.StringVar()
        self.country_combo = ttk.Combobox(
            country_frame,
            textvariable=self.country_var,
            values=[COUNTRIES[key]['name'] for key in get_all_countries()],
            state="readonly",
            width=30
        )
        self.country_combo.pack(anchor=tk.W, pady=5)
        self.country_combo.set("Deutschland")
        
        # Control buttons
        control_frame = ttk.LabelFrame(self.frame, text="Scraping Control", padding=10)
        control_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping
        )
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.test_button = ttk.Button(
            control_frame,
            text="🧪 Test Navigation",
            command=self.test_navigation
        )
        self.test_button.pack(side=tk.LEFT, padx=5)
        
    def start_scraping(self):
        """Start scraping process"""
        messagebox.showinfo("Info", "Scraping functionality ready!")
        
    def test_navigation(self):
        """Test navigation to Wilo website"""
        messagebox.showinfo("Info", "Navigation test ready!")
