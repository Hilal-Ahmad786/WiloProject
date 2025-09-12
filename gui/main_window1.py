"""
Enhanced Main Window with dual scraper support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from gui.widgets.progress_tracker import ProgressTracker
from gui.widgets.results_table import ResultsTable
from gui.widgets.shopify_config import ShopifyConfig
from gui.widgets.enhanced_scraper_controller import EnhancedScraperController
from utils.logger import get_logger, LogCapture, GUILogHandler

class MainWindow:
    """Enhanced main application window with dual scraper support"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize variables
        self.scraped_products = []
        
        # Setup logging for GUI
        self.log_capture = LogCapture()
        self.gui_log_handler = GUILogHandler(self.log_capture)
        self.logger.addHandler(self.gui_log_handler)
        
        # Setup window
        self._setup_window()
        
        # Create GUI components
        self._create_widgets()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Wilo Product Scraper & Shopify Uploader - Enhanced Edition")
        self.root.geometry("1400x900")
        self.root.minsize(1000, 700)
        
        # Center window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() - self.root.winfo_width()) // 2
        y = (self.root.winfo_screenheight() - self.root.winfo_height()) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def _create_widgets(self):
        """Create main widgets"""
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tab frames
        self.main_frame = ttk.Frame(self.notebook)
        self.shopify_frame = ttk.Frame(self.notebook)
        self.results_frame = ttk.Frame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.main_frame, text="🚀 Enhanced Scraper")
        self.notebook.add(self.shopify_frame, text="🛒 Shopify Integration")
        self.notebook.add(self.results_frame, text="📊 Results & Export")
        
        # Create main tab content
        self._create_main_tab()
        
        # Create Shopify tab content
        self._create_shopify_tab()
        
        # Create results tab content
        self._create_results_tab()
        
        # Create status bar
        self.status_var = tk.StringVar()
        self.status_var.set("Ready - Choose between Catalog or Original scraper")
        
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_main_tab(self):
        """Create main scraping tab with enhanced controller"""
        
        # Left panel for enhanced controls
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Enhanced scraper controller
        self.scraper_controller = EnhancedScraperController(left_panel, self.settings)
        self.scraper_controller.pack(fill=tk.X, pady=5)
        
        # Set callbacks
        self.scraper_controller.set_progress_callback(self.update_progress)
        self.scraper_controller.set_products_callback(self.add_product)
        
        # Quick actions
        quick_frame = ttk.LabelFrame(left_panel, text="Quick Actions", padding=10)
        quick_frame.pack(fill=tk.X, pady=5)
        
        self.upload_button = ttk.Button(
            quick_frame,
            text="🛒 Upload to Shopify",
            command=self.quick_shopify_upload,
            state=tk.DISABLED
        )
        self.upload_button.pack(fill=tk.X, pady=2)
        
        ttk.Button(
            quick_frame,
            text="📊 View Results",
            command=self.view_results
        ).pack(fill=tk.X, pady=2)
        
        ttk.Button(
            quick_frame,
            text="🗑️ Clear All",
            command=self.clear_all_results
        ).pack(fill=tk.X, pady=2)
        
        # Product statistics
        stats_frame = ttk.LabelFrame(left_panel, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=6, state='disabled')
        self.stats_text.pack(fill=tk.X)
        
        # Right panel for progress and logs
        right_panel = ttk.Frame(self.main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress tracker
        self.progress_tracker = ProgressTracker(right_panel, self.log_capture)
        self.progress_tracker.pack(fill=tk.BOTH, expand=True)
    
    def _create_shopify_tab(self):
        """Create Shopify integration tab"""
        
        # Enhanced Shopify configuration
        self.shopify_config = ShopifyConfig(self.shopify_frame, self.settings)
        self.shopify_config.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Connect scraped products getter
        self.shopify_config.set_scraped_products_getter(lambda: self.scraped_products)
    
    def _create_results_tab(self):
        """Create results tab"""
        
        # Results table
        self.results_table = ResultsTable(self.results_frame)
        self.results_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Export and action buttons
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            export_frame,
            text="📄 Export to CSV",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="📋 Export to JSON",
            command=self.export_json
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🗑️ Clear Results",
            command=self.clear_results
        ).pack(side=tk.LEFT, padx=5)
        
        # Results summary
        summary_frame = ttk.LabelFrame(self.results_frame, text="Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=8, state='disabled')
        self.summary_text.pack(fill=tk.X)
    
    def update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.status_var.set(message)
        self.progress_tracker.update_progress(message, start_progress, stop_progress)
    
    def add_product(self, product_data):
        """Add product to results"""
        self.scraped_products.append(product_data)
        self.results_table.add_product(product_data)
        self._update_statistics()
        
        # Enable upload button if we have products
        if len(self.scraped_products) > 0:
            self.upload_button.config(state=tk.NORMAL)
    
    def _update_statistics(self):
        """Update statistics display"""
        try:
            if not self.scraped_products:
                return
            
            # Calculate statistics
            total_products = len(self.scraped_products)
            catalog_products = sum(1 for p in self.scraped_products if p.get('source') == 'catalog')
            original_products = total_products - catalog_products
            
            categories = set(p.get('category', 'Unknown') for p in self.scraped_products)
            
            # Update stats text - FIXED F-STRING
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            
            stats = f"Total Products: {total_products}\n"
            stats += f"Catalog Products: {catalog_products}\n" 
            stats += f"Original Products: {original_products}\n"
            stats += f"Unique Categories: {len(categories)}\n"
            
            if self.scraped_products:
                last_product = self.scraped_products[-1]
                stats += f"Last Added: {last_product.get('name', 'Unknown')[:30]}..."
            
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def quick_shopify_upload(self):
        """Quick Shopify upload"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Products", "No products to upload.")
                return
            
            # Switch to Shopify tab
            self.notebook.select(1)
            
            # Show upload confirmation - FIXED F-STRING
            catalog_count = sum(1 for p in self.scraped_products if p.get('source') == 'catalog')
            original_count = sum(1 for p in self.scraped_products if p.get('source') != 'catalog')
            
            message = f"Upload {len(self.scraped_products)} products to Shopify?\n\n"
            message += f"Catalog products: {catalog_count}\n"
            message += f"Original products: {original_count}"
            
            result = messagebox.askyesno("Quick Upload", message)
            
            if result:
                self.shopify_config.upload_scraped_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Quick upload failed: {e}")
    
    def view_results(self):
        """View detailed results"""
        self.scraper_controller.show_results()
    
    def clear_all_results(self):
        """Clear all results"""
        try:
            if not self.scraped_products:
                messagebox.showinfo("No Data", "No products to clear.")
                return
            
            message = f"Clear all {len(self.scraped_products)} scraped products?\n\nThis cannot be undone."
            result = messagebox.askyesno("Clear All Results", message)
            
            if result:
                self.scraped_products.clear()
                self.scraper_controller.clear_results()
                self.results_table.clear()
                self._update_statistics()
                self.upload_button.config(state=tk.DISABLED)
                self.status_var.set("All results cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import csv
            from datetime import datetime
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"wilo_products_{timestamp}.csv"
            
            file_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                initialvalue=default_filename,
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'source', 'category', 'subcategory', 'short_description', 'price', 'country', 'status']
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for product in self.scraped_products:
                    row = {field: product.get(field, '') for field in fieldnames}
                    writer.writerow(row)
            
            messagebox.showinfo("Export Complete", f"✅ Exported {len(self.scraped_products)} products to CSV!")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ CSV export failed: {e}")
    
    def export_json(self):
        """Export results to JSON"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import json
            from datetime import datetime
            
            # Generate filename with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_filename = f"wilo_products_{timestamp}.json"
            
            file_path = filedialog.asksaveasfilename(
                title="Export to JSON",
                defaultextension=".json",
                initialvalue=default_filename,
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.scraped_products, f, indent=2, ensure_ascii=False)
            
            messagebox.showinfo("Export Complete", f"✅ Exported {len(self.scraped_products)} products to JSON!")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ JSON export failed: {e}")
    
    def clear_results(self):
        """Clear results table"""
        try:
            message = "Clear results table?\n\nThis will not affect scraped products."
            result = messagebox.askyesno("Clear Results", message)
            
            if result:
                self.results_table.clear()
                self.status_var.set("Results table cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
