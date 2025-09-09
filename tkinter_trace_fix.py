#!/usr/bin/env python3
"""
Fix Tkinter trace method compatibility issues
"""

def fix_main_window():
    """Fix the main_window.py file to use correct trace method"""
    
    main_window_content = '''"""
Main GUI window for Wilo scraper application
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
    """Main application window"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        # Initialize variables
        self.scraper = None
        self.is_scraping = False
        self.scraped_products = []
        
        # Setup logging for GUI
        self.log_capture = LogCapture()
        self.gui_log_handler = GUILogHandler(self.log_capture)
        self.logger.addHandler(self.gui_log_handler)
        
        # Setup window
        self._setup_window()
        
        # Create GUI components
        self._create_widgets()
        
        # Connect signals - AFTER all widgets are created
        self._connect_signals()
    
    def _setup_window(self):
        """Setup main window properties"""
        self.root.title("Wilo Product Scraper Dashboard")
        self.root.geometry("1200x800")
        self.root.minsize(800, 600)
        
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
        self.config_frame = ttk.Frame(self.notebook)
        self.results_frame = ttk.Frame(self.notebook)
        
        # Add tabs
        self.notebook.add(self.main_frame, text="Main Scraper")
        self.notebook.add(self.config_frame, text="Configuration")
        self.notebook.add(self.results_frame, text="Results")
        
        # Create main tab content
        self._create_main_tab()
        
        # Create config tab content
        self._create_config_tab()
        
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
        control_frame = ttk.LabelFrame(left_panel, text="Controls", padding=10)
        control_frame.pack(fill=tk.X, pady=5)
        
        self.start_button = ttk.Button(
            control_frame,
            text="🚀 Start Scraping",
            command=self.start_scraping,
            style="Accent.TButton"
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
        
        # Right panel for progress
        right_panel = ttk.Frame(self.main_frame)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Progress tracker
        self.progress_tracker = ProgressTracker(right_panel, self.log_capture)
        self.progress_tracker.pack(fill=tk.BOTH, expand=True)
    
    def _create_config_tab(self):
        """Create configuration tab"""
        
        # Shopify configuration
        self.shopify_config = ShopifyConfig(self.config_frame, self.settings)
        self.shopify_config.pack(fill=tk.X, padx=10, pady=5)
        
        # Scraping settings
        settings_frame = ttk.LabelFrame(self.config_frame, text="Scraping Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Max products
        max_products_frame = ttk.Frame(settings_frame)
        max_products_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(max_products_frame, text="Max products per category:").pack(side=tk.LEFT)
        
        self.max_products_var = tk.StringVar(value=str(self.settings.max_products_per_category))
        max_products_spinbox = ttk.Spinbox(
            max_products_frame,
            from_=10,
            to=1000,
            textvariable=self.max_products_var,
            width=10
        )
        max_products_spinbox.pack(side=tk.RIGHT)
        
        # Download images checkbox
        self.include_images_var = tk.BooleanVar(value=self.settings.download_images)
        ttk.Checkbutton(
            settings_frame,
            text="Download product images",
            variable=self.include_images_var
        ).pack(anchor=tk.W, pady=5)
        
        # Save settings button
        ttk.Button(
            settings_frame,
            text="💾 Save Settings",
            command=self.save_settings
        ).pack(pady=10)
    
    def _create_results_tab(self):
        """Create results tab"""
        
        # Results table
        self.results_table = ResultsTable(self.results_frame)
        self.results_table.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Export buttons
        export_frame = ttk.Frame(self.results_frame)
        export_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Button(
            export_frame,
            text="📄 Export CSV",
            command=self.export_csv
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="📋 Export JSON",
            command=self.export_json
        ).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(
            export_frame,
            text="🛒 Upload to Shopify",
            command=self.upload_to_shopify
        ).pack(side=tk.LEFT, padx=5)
    
    def _connect_signals(self):
        """Connect widget signals - FIXED for modern Tkinter"""
        try:
            # Use trace_add instead of trace for newer Tkinter versions
            if hasattr(self.max_products_var, 'trace_add'):
                self.max_products_var.trace_add('write', self._on_max_products_changed)
                self.include_images_var.trace_add('write', self._on_include_images_changed)
            else:
                # Fallback for older Tkinter versions
                self.max_products_var.trace('w', self._on_max_products_changed)
                self.include_images_var.trace('w', self._on_include_images_changed)
        except Exception as e:
            self.logger.warning(f"Could not set up variable traces: {e}")
    
    def _on_max_products_changed(self, *args):
        """Handle max products setting change"""
        try:
            value = int(self.max_products_var.get())
            self.settings.scraping.max_products_per_category = value
            self.settings.max_products_per_category = value  # Legacy compatibility
        except ValueError:
            pass
    
    def _on_include_images_changed(self, *args):
        """Handle include images setting change"""
        self.settings.scraping.download_images = self.include_images_var.get()
        self.settings.download_images = self.include_images_var.get()  # Legacy compatibility
    
    def start_scraping(self):
        """Start the scraping process"""
        if self.is_scraping:
            return
        
        try:
            # Get selected country
            country_key = self.country_selector.get_selected_country_key()
            
            # Update browser settings
            browser_settings = self.browser_settings.get_settings()
            self.settings.scraping.headless_mode = browser_settings['headless_mode']
            self.settings.scraping.timeout = browser_settings['browser_timeout']
            self.settings.scraping.delay_between_actions = browser_settings['page_load_delay']
            
            # Update legacy properties
            self.settings.headless_mode = browser_settings['headless_mode']
            self.settings.browser_timeout = browser_settings['browser_timeout']
            self.settings.page_load_delay = browser_settings['page_load_delay']
            
            # Create scraper
            self.scraper = WiloScraper(self.settings)
            
            # Set callbacks
            self.scraper.set_progress_callback(self.progress_tracker.update_progress)
            self.scraper.set_products_callback(self.results_table.add_product)
            
            # Update UI
            self.is_scraping = True
            self.start_button.config(state=tk.DISABLED)
            self.stop_button.config(state=tk.NORMAL)
            self.status_var.set("Scraping in progress...")
            
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
        """Worker function for scraping thread"""
        try:
            products = self.scraper.start_scraping(country_key)
            self.scraped_products.extend(products)
            
            # Update UI on main thread
            self.root.after(0, self._on_scraping_completed, len(products))
            
        except Exception as e:
            self.logger.error(f"Scraping worker failed: {e}")
            self.root.after(0, self._on_scraping_failed, str(e))
    
    def _on_scraping_completed(self, product_count):
        """Handle scraping completion"""
        self.status_var.set(f"Scraping completed! Found {product_count} products")
        self._reset_scraping_ui()
        messagebox.showinfo("Success", f"Scraping completed! Found {product_count} products")
    
    def _on_scraping_failed(self, error_message):
        """Handle scraping failure"""
        self.status_var.set("Scraping failed")
        self._reset_scraping_ui()
        messagebox.showerror("Error", f"Scraping failed: {error_message}")
    
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
            messagebox.showinfo("Success", "Navigation test successful!")
        else:
            self.status_var.set("Navigation test failed")
            messagebox.showerror("Error", "Navigation test failed")
    
    def _on_navigation_test_failed(self, error_message):
        """Handle navigation test failure"""
        self.status_var.set("Navigation test failed")
        messagebox.showerror("Error", f"Navigation test failed: {error_message}")
    
    def save_settings(self):
        """Save current settings"""
        try:
            # Update settings from GUI
            self.settings.scraping.max_products_per_category = int(self.max_products_var.get())
            self.settings.scraping.download_images = self.include_images_var.get()
            
            # Update Shopify settings
            shopify_settings = self.shopify_config.get_settings()
            self.settings.shopify.shop_url = shopify_settings['shop_url']
            self.settings.shopify.access_token = shopify_settings['access_token']
            
            # Save to file
            self.settings.save()
            
            self.status_var.set("Settings saved successfully")
            messagebox.showinfo("Success", "Settings saved successfully!")
            
        except Exception as e:
            self.logger.error(f"Failed to save settings: {e}")
            messagebox.showerror("Error", f"Failed to save settings: {e}")
    
    def export_csv(self):
        """Export results to CSV"""
        try:
            products = self.results_table.get_all_products()
            if not products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            # TODO: Implement CSV export
            messagebox.showinfo("Info", "CSV export functionality to be implemented")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def export_json(self):
        """Export results to JSON"""
        try:
            products = self.results_table.get_all_products()
            if not products:
                messagebox.showwarning("No Data", "No products to export")
                return
            
            # TODO: Implement JSON export
            messagebox.showinfo("Info", "JSON export functionality to be implemented")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {e}")
    
    def upload_to_shopify(self):
        """Upload products to Shopify"""
        try:
            products = self.results_table.get_all_products()
            if not products:
                messagebox.showwarning("No Data", "No products to upload")
                return
            
            # TODO: Implement Shopify upload
            messagebox.showinfo("Info", "Shopify upload functionality to be implemented")
            
        except Exception as e:
            messagebox.showerror("Error", f"Upload failed: {e}")
    
    def update_status(self, message):
        """Update status bar"""
        self.status_var.set(message)
        self.root.update_idletasks()
'''
    
    with open('gui/main_window.py', 'w') as f:
        f.write(main_window_content)
    
    print("✅ Fixed gui/main_window.py - Updated trace method for modern Tkinter")

def main():
    """Main fix function"""
    print("🔧 Fixing Tkinter Trace Method Issues")
    print("=" * 40)
    
    # Fix main window
    fix_main_window()
    
    print("\n✅ Tkinter compatibility issues fixed!")
    print("\n🎯 Try running the application:")
    print("python main.py")

if __name__ == "__main__":
    main()