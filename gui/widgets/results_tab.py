"""
Results display tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.logger import get_logger

class ResultsTab:
    """Results display tab"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.logger = get_logger(__name__)
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
    def create_widgets(self):
        """Create results widgets"""
        
        # Summary section
        summary_frame = ttk.LabelFrame(self.frame, text="Scraping Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=5, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.X)
        
        # Export buttons
        export_frame = ttk.Frame(self.frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            export_frame,
            text="📄 Export to CSV",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🛒 Upload to Shopify",
            command=self.upload_to_shopify
        ).pack(side=tk.LEFT, padx=5)
        
    def export_csv(self):
        """Export results to CSV"""
        messagebox.showinfo("Info", "CSV export ready!")
            
    def upload_to_shopify(self):
        """Upload products to Shopify"""
        messagebox.showinfo("Info", "Shopify upload ready!")
