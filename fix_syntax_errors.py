#!/usr/bin/env python3
"""
Single-shot fix for syntax errors in Wilo scraper project
Fixes f-string and other syntax issues
"""

def fix_main_window():
    """Fix syntax errors in gui/main_window.py"""
    
    fixed_content = '''"""
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
            
            stats = f"Total Products: {total_products}\\n"
            stats += f"Catalog Products: {catalog_products}\\n" 
            stats += f"Original Products: {original_products}\\n"
            stats += f"Unique Categories: {len(categories)}\\n"
            
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
            
            message = f"Upload {len(self.scraped_products)} products to Shopify?\\n\\n"
            message += f"Catalog products: {catalog_count}\\n"
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
            
            message = f"Clear all {len(self.scraped_products)} scraped products?\\n\\nThis cannot be undone."
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
            message = "Clear results table?\\n\\nThis will not affect scraped products."
            result = messagebox.askyesno("Clear Results", message)
            
            if result:
                self.results_table.clear()
                self.status_var.set("Results table cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
'''
    
    with open('gui/main_window.py', 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed gui/main_window.py")

def fix_enhanced_controller():
    """Fix any syntax errors in enhanced_scraper_controller.py"""
    
    fixed_content = '''"""
Enhanced scraper controller widget with dual scraper support
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from scraper.wilo_scraper import WiloScraper
from scraper.wilo_catalog_scraper import WiloCatalogScraper
from gui.widgets.country_selector import CountrySelector
from gui.widgets.browser_settings import BrowserSettings

class EnhancedScraperController(ttk.LabelFrame):
    """Enhanced controller for both original and catalog scrapers"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Enhanced Scraping Controls", padding="10")
        
        self.parent = parent
        self.settings = settings
        self.scraped_products = []
        
        # Scraper instances
        self.original_scraper = None
        self.catalog_scraper = None
        self.is_scraping = False
        
        # Callbacks
        self.progress_callback = None
        self.products_callback = None
        
        self._create_widgets()
    
    def _create_widgets(self):
        """Create enhanced control widgets"""
        
        # Scraper Selection
        scraper_frame = ttk.LabelFrame(self, text="Scraper Selection", padding="5")
        scraper_frame.pack(fill='x', pady=5)
        
        self.scraper_type_var = tk.StringVar(value="catalog")
        
        ttk.Radiobutton(
            scraper_frame,
            text="🆕 New Catalog Scraper (wilo.com/katalog)",
            variable=self.scraper_type_var,
            value="catalog"
        ).pack(anchor='w')
        
        ttk.Radiobutton(
            scraper_frame,
            text="📊 Original Select Scraper (select.wilo.com)",
            variable=self.scraper_type_var,
            value="original"
        ).pack(anchor='w')
        
        # Country Selection (for original scraper only)
        self.country_frame = ttk.LabelFrame(self, text="Country Selection (Original Scraper Only)", padding="5")
        self.country_frame.pack(fill='x', pady=5)
        
        self.country_selector = CountrySelector(self.country_frame, self.settings)
        self.country_selector.pack(fill='x')
        
        # Product Limit Control
        limit_frame = ttk.LabelFrame(self, text="Product Extraction Limits", padding="5")
        limit_frame.pack(fill='x', pady=5)
        
        # Catalog scraper limit
        catalog_limit_frame = ttk.Frame(limit_frame)
        catalog_limit_frame.pack(fill='x', pady=2)
        
        ttk.Label(catalog_limit_frame, text="Catalog Products to Extract:").pack(side='left')
        self.catalog_limit_var = tk.StringVar(value="2")
        catalog_spinbox = ttk.Spinbox(
            catalog_limit_frame,
            from_=1,
            to=20,
            textvariable=self.catalog_limit_var,
            width=5
        )
        catalog_spinbox.pack(side='left', padx=5)
        ttk.Label(catalog_limit_frame, text="(1-20 products)").pack(side='left', padx=5)
        
        # Original scraper limit (categories)
        original_limit_frame = ttk.Frame(limit_frame)
        original_limit_frame.pack(fill='x', pady=2)
        
        ttk.Label(original_limit_frame, text="Original Categories to Process:").pack(side='left')
        self.original_limit_var = tk.StringVar(value="1")
        original_spinbox = ttk.Spinbox(
            original_limit_frame,
            from_=1,
            to=13,
            textvariable=self.original_limit_var,
            width=5
        )
        original_spinbox.pack(side='left', padx=5)
        ttk.Label(original_limit_frame, text="(1-13 categories)").pack(side='left', padx=5)
        
        # Browser Settings
        self.browser_settings = BrowserSettings(self, self.settings)
        self.browser_settings.pack(fill='x', pady=5)
        
        # Control Buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=10)
        
        self.start_button = ttk.Button(
            button_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping
        )
        self.start_button.pack(side='left', padx=5)
        
        self.stop_button = ttk.Button(
            button_frame,
            text="⏹ Stop Scraping",
            command=self.stop_scraping,
            state='disabled'
        )
        self.stop_button.pack(side='left', padx=5)
        
        self.test_button = ttk.Button(
            button_frame,
            text="🧪 Test Navigation",
            command=self.test_navigation
        )
        self.test_button.pack(side='left', padx=5)
        
        # Quick Actions
        quick_frame = ttk.Frame(self)
        quick_frame.pack(fill='x', pady=5)
        
        ttk.Button(
            quick_frame,
            text="🔄 Switch Scraper",
            command=self.switch_scraper
        ).pack(side='left', padx=5)
        
        ttk.Button(
            quick_frame,
            text="📊 Show Results",
            command=self.show_results
        ).pack(side='left', padx=5)
        
        # Status and Progress
        status_frame = ttk.LabelFrame(self, text="Status", padding="5")
        status_frame.pack(fill='x', pady=5)
        
        self.status_var = tk.StringVar(value="Ready to start scraping")
        ttk.Label(status_frame, textvariable=self.status_var).pack(anchor='w')
        
        self.progress_bar = ttk.Progressbar(status_frame, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=2)
        
        # Product Count
        count_frame = ttk.Frame(status_frame)
        count_frame.pack(fill='x', pady=2)
        
        ttk.Label(count_frame, text="Extracted Products:").pack(side='left')
        self.product_count_var = tk.StringVar(value="0")
        ttk.Label(count_frame, textvariable=self.product_count_var, font=('Arial', 12, 'bold')).pack(side='left', padx=5)
        
        # Bind scraper type change
        self.scraper_type_var.trace('w', self._on_scraper_type_changed)
        self._on_scraper_type_changed()
    
    def _on_scraper_type_changed(self, *args):
        """Handle scraper type change"""
        scraper_type = self.scraper_type_var.get()
        
        if scraper_type == "catalog":
            self.country_frame.pack_forget()
            self.status_var.set("Catalog scraper selected - extracts from wilo.com/katalog")
        else:
            self.country_frame.pack(fill='x', pady=5, before=self.browser_settings)
            self.status_var.set("Original scraper selected - extracts from select.wilo.com")
    
    def set_progress_callback(self, callback):
        """Set progress callback"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set products callback"""
        self.products_callback = callback
    
    def start_scraping(self):
        """Start the appropriate scraper"""
        if self.is_scraping:
            return
        
        try:
            scraper_type = self.scraper_type_var.get()
            
            # Update browser settings
            browser_settings = self.browser_settings.get_settings()
            self.settings.headless_mode = browser_settings['headless_mode']
            self.settings.browser_timeout = browser_settings['browser_timeout']
            self.settings.page_load_delay = browser_settings['page_load_delay']
            
            # Update UI
            self.is_scraping = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress_bar.start()
            
            if scraper_type == "catalog":
                self._start_catalog_scraping()
            else:
                self._start_original_scraping()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start scraping: {e}")
            self._reset_ui()
    
    def _start_catalog_scraping(self):
        """Start catalog scraping"""
        try:
            max_products = int(self.catalog_limit_var.get())
            
            self.catalog_scraper = WiloCatalogScraper(self.settings)
            self.catalog_scraper.set_progress_callback(self._update_progress)
            self.catalog_scraper.set_products_callback(self._add_product)
            
            self.status_var.set(f"Starting catalog scraping (max {max_products} products)...")
            
            # Start in separate thread
            thread = threading.Thread(target=self._catalog_scraping_worker, args=(max_products,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start catalog scraping: {e}")
            self._reset_ui()
    
    def _start_original_scraping(self):
        """Start original scraping"""
        try:
            country_key = self.country_selector.get_selected_country_key()
            max_categories = int(self.original_limit_var.get())
            
            self.original_scraper = WiloScraper(self.settings)
            self.original_scraper.set_progress_callback(self._update_progress)
            self.original_scraper.set_products_callback(self._add_product)
            
            self.status_var.set(f"Starting original scraping (max {max_categories} categories)...")
            
            # Start in separate thread
            thread = threading.Thread(target=self._original_scraping_worker, args=(country_key, max_categories))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to start original scraping: {e}")
            self._reset_ui()
    
    def _catalog_scraping_worker(self, max_products):
        """Worker thread for catalog scraping"""
        try:
            products = self.catalog_scraper.start_scraping(max_products)
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.after(0, self._on_scraping_completed, len(products), "catalog")
            
        except Exception as e:
            self.after(0, self._on_scraping_failed, str(e))
    
    def _original_scraping_worker(self, country_key, max_categories):
        """Worker thread for original scraping"""
        try:
            products = self.original_scraper.start_scraping(country_key)
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.after(0, self._on_scraping_completed, len(products), "original")
            
        except Exception as e:
            self.after(0, self._on_scraping_failed, str(e))
    
    def _update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.status_var.set(message)
        
        if self.progress_callback:
            self.progress_callback(message, start_progress, stop_progress)
    
    def _add_product(self, product_data):
        """Add product to results"""
        self.scraped_products.append(product_data)
        self.product_count_var.set(str(len(self.scraped_products)))
        
        if self.products_callback:
            self.products_callback(product_data)
    
    def _on_scraping_completed(self, product_count, scraper_type):
        """Handle scraping completion"""
        self._reset_ui()
        
        scraper_name = "Catalog" if scraper_type == "catalog" else "Original"
        self.status_var.set(f"{scraper_name} scraping completed! Found {product_count} products")
        
        message = f"✅ {scraper_name} scraping completed!\\n\\n"
        message += f"Found {product_count} new products\\n"
        message += f"Total products: {len(self.scraped_products)}"
        
        messagebox.showinfo("Scraping Complete", message)
    
    def _on_scraping_failed(self, error_message):
        """Handle scraping failure"""
        self._reset_ui()
        self.status_var.set("Scraping failed")
        messagebox.showerror("Error", f"❌ Scraping failed: {error_message}")
    
    def _reset_ui(self):
        """Reset UI after scraping"""
        self.is_scraping = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress_bar.stop()
    
    def stop_scraping(self):
        """Stop current scraping"""
        if self.catalog_scraper:
            self.catalog_scraper.stop()
        if self.original_scraper:
            self.original_scraper.stop()
        
        self.status_var.set("Stopping scraping...")
        self._reset_ui()
    
    def test_navigation(self):
        """Test navigation for selected scraper"""
        try:
            scraper_type = self.scraper_type_var.get()
            
            self.status_var.set("Testing navigation...")
            
            if scraper_type == "catalog":
                test_scraper = WiloCatalogScraper(self.settings)
                test_scraper.set_progress_callback(self._update_progress)
            else:
                test_scraper = WiloScraper(self.settings)
                test_scraper.set_progress_callback(self._update_progress)
            
            # Run test in separate thread
            thread = threading.Thread(target=self._test_navigation_worker, args=(test_scraper,))
            thread.daemon = True
            thread.start()
            
        except Exception as e:
            messagebox.showerror("Error", f"Navigation test failed: {e}")
    
    def _test_navigation_worker(self, test_scraper):
        """Worker for navigation test"""
        try:
            success = test_scraper.test_navigation()
            self.after(0, self._on_navigation_test_completed, success)
        except Exception as e:
            self.after(0, self._on_navigation_test_failed, str(e))
    
    def _on_navigation_test_completed(self, success):
        """Handle navigation test completion"""
        if success:
            self.status_var.set("Navigation test successful!")
            messagebox.showinfo("Success", "✅ Navigation test successful!")
        else:
            self.status_var.set("Navigation test failed")
            messagebox.showerror("Error", "❌ Navigation test failed")
    
    def _on_navigation_test_failed(self, error_message):
        """Handle navigation test failure"""
        self.status_var.set("Navigation test failed")
        messagebox.showerror("Error", f"❌ Navigation test failed: {error_message}")
    
    def switch_scraper(self):
        """Switch between scrapers"""
        current = self.scraper_type_var.get()
        new_scraper = "original" if current == "catalog" else "catalog"
        self.scraper_type_var.set(new_scraper)
        
        scraper_name = "Catalog" if new_scraper == "catalog" else "Original"
        self.status_var.set(f"Switched to {scraper_name} scraper")
    
    def show_results(self):
        """Show current results"""
        if not self.scraped_products:
            messagebox.showinfo("No Results", "No products have been scraped yet.")
            return
        
        # Create results window
        results_window = tk.Toplevel(self)
        results_window.title("Scraping Results")
        results_window.geometry("800x600")
        
        # Results text
        text_frame = ttk.Frame(results_window)
        text_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        results_text = tk.Text(text_frame, wrap='word')
        scrollbar = ttk.Scrollbar(text_frame, orient='vertical', command=results_text.yview)
        results_text.configure(yscrollcommand=scrollbar.set)
        
        results_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Display results
        header = f"=== SCRAPING RESULTS ({len(self.scraped_products)} products) ===\\n\\n"
        results_text.insert('1.0', header)
        
        for i, product in enumerate(self.scraped_products, 1):
            results_text.insert('end', f"{i}. {product.get('name', 'Unknown')}\\n")
            results_text.insert('end', f"   Source: {product.get('source', 'unknown')}\\n")
            results_text.insert('end', f"   Category: {product.get('category', 'Unknown')}\\n")
            if product.get('short_description'):
                desc = product['short_description'][:100] + "..." if len(product['short_description']) > 100 else product['short_description']
                results_text.insert('end', f"   Description: {desc}\\n")
            results_text.insert('end', "\\n")
        
        results_text.config(state='disabled')
    
    def get_scraped_products(self):
        """Get all scraped products"""
        return self.scraped_products
    
    def clear_results(self):
        """Clear all scraped products"""
        self.scraped_products.clear()
        self.product_count_var.set("0")
        self.status_var.set("Results cleared")
'''
    
    with open('gui/widgets/enhanced_scraper_controller.py', 'w') as f:
        f.write(fixed_content)
    
    print("✅ Fixed gui/widgets/enhanced_scraper_controller.py")

def main():
    """Main fix function"""
    print("🔧 FIXING SYNTAX ERRORS - Single Shot Solution")
    print("=" * 60)
    
    try:
        # Fix main window
        fix_main_window()
        
        # Fix enhanced controller
        fix_enhanced_controller()
        
        print("\n✅ ALL SYNTAX ERRORS FIXED!")
        print("\n🎯 Fixed Issues:")
        print("• Unterminated f-string literals")
        print("• Proper newline escaping in f-strings")
        print("• Multi-line string concatenation")
        print("• Proper string formatting")
        
        print("\n🚀 Your application should now run:")
        print("python main.py")
        
    except Exception as e:
        print(f"❌ Error during fix: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())