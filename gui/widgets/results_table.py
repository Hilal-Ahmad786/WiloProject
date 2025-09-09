"""
Results table widget
"""

import tkinter as tk
from tkinter import ttk

class ResultsTable(ttk.LabelFrame):
    """Widget for displaying scraping results"""
    
    def __init__(self, parent):
        super().__init__(parent, text="Scraped Products", padding="10")
        self.total_products = 0
        self._create_widgets()
    
    def _create_widgets(self):
        """Create results table widgets"""
        # Summary frame
        summary_frame = ttk.Frame(self)
        summary_frame.pack(fill='x', pady=5)
        
        ttk.Label(summary_frame, text="Total Products:").pack(side='left')
        self.total_label = ttk.Label(summary_frame, text="0", font=('Arial', 12, 'bold'))
        self.total_label.pack(side='left', padx=10)
        
        # Create treeview table
        columns = ('Name', 'Category', 'Price', 'Country', 'Status')
        self.tree = ttk.Treeview(self, columns=columns, show='headings', height=15)
        
        # Configure columns
        for col in columns:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=150)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tree.yview)
        h_scrollbar = ttk.Scrollbar(self, orient='horizontal', command=self.tree.xview)
        
        self.tree.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        
        # Pack widgets
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill='both', expand=True, pady=5)
        
        self.tree.pack(side='left', fill='both', expand=True)
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
    
    def add_product(self, product_data):
        """Add product to results table"""
        self.tree.insert('', 'end', values=(
            product_data.get('name', 'Unknown'),
            product_data.get('category', 'Unknown'),
            product_data.get('price', 'N/A'),
            product_data.get('country', 'Unknown'),
            product_data.get('status', 'Scraped')
        ))
        
        self.total_products += 1
        self.total_label.config(text=str(self.total_products))
    
    def clear(self):
        """Clear all results"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.total_products = 0
        self.total_label.config(text="0")
    
    def get_all_products(self):
        """Get all products from table"""
        products = []
        for item in self.tree.get_children():
            values = self.tree.item(item)['values']
            products.append({
                'name': values[0],
                'category': values[1],
                'price': values[2],
                'country': values[3],
                'status': values[4]
            })
        return products
