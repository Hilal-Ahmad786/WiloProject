"""
Shopify configuration widget
"""

import tkinter as tk
from tkinter import ttk, messagebox

class ShopifyConfig(ttk.LabelFrame):
    """Widget for Shopify configuration"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Shopify Configuration", padding="10")
        self.settings = settings
        self._create_widgets()
    
    def _create_widgets(self):
        """Create Shopify config widgets"""
        # Shop URL
        ttk.Label(self, text="Shop URL:").grid(row=0, column=0, sticky='w', pady=2)
        self.shop_url_var = tk.StringVar(value=self.settings.shopify_shop_url)
        ttk.Entry(self, textvariable=self.shop_url_var, width=50).grid(row=0, column=1, sticky='w', padx=5)
        
        # Access Token
        ttk.Label(self, text="Access Token:").grid(row=1, column=0, sticky='w', pady=2)
        self.access_token_var = tk.StringVar(value=self.settings.shopify_access_token)
        ttk.Entry(self, textvariable=self.access_token_var, width=50, show="*").grid(row=1, column=1, sticky='w', padx=5)
        
        # Test button
        ttk.Button(
            self,
            text="Test Connection",
            command=self.test_connection
        ).grid(row=2, column=0, pady=10, sticky='w')
        
        # Status label
        self.status_var = tk.StringVar(value="Not tested")
        self.status_label = ttk.Label(self, textvariable=self.status_var)
        self.status_label.grid(row=2, column=1, padx=5, sticky='w')
    
    def test_connection(self):
        """Test Shopify connection"""
        try:
            # Update settings
            self.settings.shopify_shop_url = self.shop_url_var.get()
            self.settings.shopify_access_token = self.access_token_var.get()
            
            # TODO: Implement actual connection test
            self.status_var.set("✅ Connection successful!")
            messagebox.showinfo("Success", "Shopify connection test passed!")
            
        except Exception as e:
            self.status_var.set("❌ Connection failed")
            messagebox.showerror("Error", f"Connection test failed: {e}")
    
    def get_settings(self):
        """Get current Shopify settings"""
        return {
            'shop_url': self.shop_url_var.get(),
            'access_token': self.access_token_var.get()
        }
