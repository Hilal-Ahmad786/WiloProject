"""
Enhanced Main Window with Shopify Integration
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
from typing import Optional

from gui.widgets.country_selector import CountrySelector
from gui.widgets.browser_settings import BrowserSettings
from gui.widgets.progress_tracker import ProgressTracker
from gui.widgets.results_table import ResultsTable
from gui.widgets.shopify_config import ShopifyConfig
from scraper.wilo_scraper import WiloScraper
from utils.logger import get_logger, LogCapture, GUILogHandler

class MainWindow:
    """Enhanced main application window with Shopify integration"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize variables
        self.scraper = None
        self.is_scraping = False
        self.scraped_products = []  # Store all scraped products
        
        # Setup logging for GUI
        self.log_capture = LogCapture()
        self.gui_log_handler = GUILogHandler(self.log_capture)
        self.logger.addHandler(self.gui_log_handler)
        
        # Setup window
        self._setup_window()
        
        # Create GUI components
        self._create_widgets()
        
        # Connect signals
        self._connect_signals()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Wilo Product Scraper & Shopify Uploader")
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
        self.notebook.add(self.main_frame, text="🚀 Main Scraper")
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
        self.status_var.set("Ready")
        
        self.status_bar = ttk.Label(
            self.root,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def _create_main_tab(self):
        """Create main scraping tab"""
        
        # Left panel for controls
        left_panel = ttk.Frame(self.main_frame)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=5, pady=5)
        
        # Country selector
        self.country_selector = CountrySelector(left_panel, self.settings)
        self.country_selector.pack(fill=tk.X, pady=5)
        
        # Browser settings
        self.browser_settings = BrowserSettings(left_panel, self.settings)
        self.browser_settings.pack(fill=tk.X, pady=5)
        
        # Control buttons
        control_frame = ttk.LabelFrame(left_panel, text="Scraping Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping
        )
        self.start_button.pack(fill=tk.X, pady=2)
        
        self.stop_button = ttk.Button(
            control_frame,
            text="⏹ Stop Scraping",
            command=self.stop_scraping,
            state=tk.DISABLED
        )
        self.stop_button.pack(fill=tk.X, pady=2)
        
        self.test_button = ttk.Button(
            control_frame,
            text="🧪 Test Navigation",
            command=self.test_navigation
        )
        self.test_button.pack(fill=tk.X, pady=2)
        
        # Quick Shopify upload
        shopify_quick_frame = ttk.LabelFrame(left_panel, text="Quick Shopify Upload", padding=10)
        shopify_quick_frame.pack(fill=tk.X, pady=5)
        
        self.quick_upload_button = ttk.Button(
            shopify_quick_frame,
            text="🛒 Upload to Shopify",
            command=self.quick_shopify_upload,
            state=tk.DISABLED
        )
        self.quick_upload_button.pack(fill=tk.X, pady=2)
        
        # Product count display
        count_frame = ttk.LabelFrame(left_panel, text="Product Count", padding=10)
        count_frame.pack(fill=tk.X, pady=5)
        
        self.product_count_var = tk.StringVar(value="0 products scraped")
        ttk.Label(count_frame, textvariable=self.product_count_var, font=('Arial', 12, 'bold')).pack()
        
        # Right panel for progress
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
        
        # Statistics frame
        stats_frame = ttk.LabelFrame(self.results_frame, text="Statistics", padding=10)
        stats_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.stats_text = tk.Text(stats_frame, height=4, state='disabled')
        self.stats_text.pack(fill=tk.X)
    
    def _connect_signals(self):
        """Connect widget signals"""
        try:
            # Variable tracing for settings
            if hasattr(tk.StringVar, 'trace_add'):
                # Modern Tkinter
                pass  # Add traces if needed
            else:
                # Older Tkinter
                pass
        except Exception as e:
            self.logger.warning(f"Could not set up variable traces: {e}")
    
    def start_scraping(self):
        """Start the enhanced scraping process"""
        if self.is_scraping:
            return
        
        try:
            # Get selected country
            country_key = self.country_selector.get_selected_country_key()
            
            # Update browser settings
            browser_settings = self.browser_settings.get_settings()
            self.settings.headless_mode = browser_settings['headless_mode']
            self.settings.browser_timeout = browser_settings['browser_timeout']
            self.settings.page_load_delay = browser_settings['page_load_delay']
            
            # Create enhanced scraper
            self.scraper = WiloScraper(self.settings)
            
            # Set callbacks
            self.scraper.set_progress_callback(self.progress_tracker.update_progress)
            self.scraper.set_products_callback(self.add_product)
            
            # Update UI
            self.is_scraping = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Enhanced scraping in progress...")
            
            # Start scraping in separate thread
            self.scraping_thread = threading.Thread(
                target=self._scraping_worker,
                args=(country_key,)
            )
            self.scraping_thread.daemon = True
            self.scraping_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start scraping: {e}")
            messagebox.showerror("Error", f"Failed to start scraping: {e}")
            self._reset_scraping_ui()
    
    def _scraping_worker(self, country_key):
        """Enhanced worker function for scraping thread"""
        try:
            products = self.scraper.start_scraping(country_key)
            
            # Store products
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.root.after(0, self._on_scraping_completed, len(products))
            
        except Exception as e:
            self.logger.error(f"Scraping worker failed: {e}")
            self.root.after(0, self._on_scraping_failed, str(e))
    
    def _on_scraping_completed(self, product_count):
        """Handle enhanced scraping completion"""
        self.status_var.set(f"Enhanced scraping completed! Found {product_count} products")
        self._reset_scraping_ui()
        self._update_product_count()
        self._update_statistics()
        
        # Enable Shopify upload if products were found
        if product_count > 0:
            self.quick_upload_button.config(state=tk.NORMAL)
        
        messagebox.showinfo("Success", f"✅ Enhanced scraping completed!\n\nFound {product_count} products\nTotal products: {len(self.scraped_products)}")
    
    def _on_scraping_failed(self, error_message):
        """Handle scraping failure"""
        self.status_var.set("Scraping failed")
        self._reset_scraping_ui()
        messagebox.showerror("Error", f"❌ Scraping failed: {error_message}")
    
    def add_product(self, product_data):
        """Add product to results (enhanced)"""
        # Add to results table
        self.results_table.add_product(product_data)
        
        # Update count
        self._update_product_count()
    
    def _update_product_count(self):
        """Update product count display"""
        count = len(self.scraped_products)
        self.product_count_var.set(f"{count} products scraped")
    
    def _update_statistics(self):
        """Update statistics display"""
        try:
            if not self.scraped_products:
                return
            
            # Calculate statistics
            total_products = len(self.scraped_products)
            categories = set(p.get('category', 'Unknown') for p in self.scraped_products)
            subcategories = set(p.get('subcategory', 'Unknown') for p in self.scraped_products)
            
            # Update stats text
            self.stats_text.config(state='normal')
            self.stats_text.delete(1.0, tk.END)
            
            stats = f"Total Products: {total_products}\n"
            stats += f"Categories: {len(categories)}\n"
            stats += f"Subcategories: {len(subcategories)}\n"
            stats += f"Average per Category: {total_products / len(categories):.1f}"
            
            self.stats_text.insert(1.0, stats)
            self.stats_text.config(state='disabled')
            
        except Exception as e:
            self.logger.error(f"Error updating statistics: {e}")
    
    def quick_shopify_upload(self):
        """Quick Shopify upload from main tab"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Products", "No products to upload. Please scrape some products first.")
                return
            
            # Switch to Shopify tab
            self.notebook.select(1)
            
            # Show upload confirmation
            result = messagebox.askyesno(
                "Quick Upload", 
                f"Upload {len(self.scraped_products)} scraped products to Shopify?\n\nThis will use your current Shopify settings."
            )
            
            if result:
                # Trigger upload on Shopify tab
                self.shopify_config.upload_scraped_products()
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Quick upload failed: {e}")
    
    def stop_scraping(self):
        """Stop the scraping process"""
        if self.scraper:
            self.scraper.stop()
        
        self.status_var.set("Stopping scraping...")
        self._reset_scraping_ui()
    
    def _reset_scraping_ui(self):
        """Reset UI after scraping"""
        self.is_scraping = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
    
    def test_navigation(self):
        """Test navigation to Wilo website"""
        try:
            self.status_var.set("Testing navigation...")
            
            # Create temporary scraper
            test_scraper = WiloScraper(self.settings)
            test_scraper.set_progress_callback(self.progress_tracker.update_progress)
            
            # Run test in separate thread
            test_thread = threading.Thread(target=self._test_navigation_worker, args=(test_scraper,))
            test_thread.daemon = True
            test_thread.start()
            
        except Exception as e:
            self.logger.error(f"Failed to start navigation test: {e}")
            messagebox.showerror("Error", f"Navigation test failed: {e}")
    
    def _test_navigation_worker(self, test_scraper):
        """Worker function for navigation test"""
        try:
            success = test_scraper.test_navigation()
            
            # Update UI on main thread
            self.root.after(0, self._on_navigation_test_completed, success)
            
        except Exception as e:
            self.logger.error(f"Navigation test worker failed: {e}")
            self.root.after(0, self._on_navigation_test_failed, str(e))
    
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
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            if not self.scraped_products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            from tkinter import filedialog
            import csv
            
            file_path = filedialog.asksaveasfilename(
                title="Export to CSV",
                defaultextension=".csv",
                filetypes=[("CSV files", "*.csv"), ("All files", "*.*")]
            )
            
            if not file_path:
                return
            
            # Export to CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as f:
                fieldnames = ['name', 'category', 'subcategory', 'price', 'description', 'country', 'status']
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
            
            file_path = filedialog.asksaveasfilename(
                title="Export to JSON",
                defaultextension=".json",
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
        """Clear all results"""
        try:
            result = messagebox.askyesno("Clear Results", "Clear all scraped products?\n\nThis cannot be undone.")
            
            if result:
                self.scraped_products.clear()
                self.results_table.clear()
                self._update_product_count()
                self._update_statistics()
                self.quick_upload_button.config(state=tk.DISABLED)
                self.status_var.set("Results cleared")
            
        except Exception as e:
            messagebox.showerror("Error", f"❌ Failed to clear results: {e}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
