"""
Configuration tab
"""

import tkinter as tk
from tkinter import ttk, messagebox
from utils.logger import get_logger

class ConfigTab:
    """Configuration tab"""
    
    def __init__(self, parent, settings):
        self.parent = parent
        self.settings = settings
        self.logger = get_logger(__name__)
        
        self.frame = ttk.Frame(parent)
        self.create_widgets()
        
    def create_widgets(self):
        """Create configuration widgets"""
        
        # Shopify settings
        shopify_frame = ttk.LabelFrame(self.frame, text="Shopify Configuration", padding=10)
        shopify_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(shopify_frame, text="Shop URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.shop_url_var = tk.StringVar(value=self.settings.shopify_shop_url)
        ttk.Entry(shopify_frame, textvariable=self.shop_url_var, width=50).grid(row=0, column=1, sticky=tk.W, padx=5)
        
        ttk.Button(
            shopify_frame,
            text="Test Connection",
            command=self.test_shopify_connection
        ).grid(row=1, column=0, pady=10, sticky=tk.W)
        
    def test_shopify_connection(self):
        """Test Shopify API connection"""
        messagebox.showinfo("Info", "Shopify connection test ready!")
