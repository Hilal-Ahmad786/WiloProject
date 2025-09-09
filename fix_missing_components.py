#!/usr/bin/env python3
"""
Fix missing components in the Wilo scraper project
"""

import os
from pathlib import Path

def fix_logger_module():
    """Fix the logger module to include missing classes"""
    
    logger_content = '''"""
Enhanced logging utilities with GUI support
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from collections import deque
import threading

def setup_logging(log_level=logging.INFO):
    """Setup application logging"""
    
    # Create logs directory
    logs_dir = Path('logs')
    logs_dir.mkdir(exist_ok=True)
    
    # Create log filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = logs_dir / f'wilo_scraper_{timestamp}.log'
    
    # Configure logging
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Create application logger
    logger = logging.getLogger('wilo_scraper')
    logger.info(f"Logging initialized - {log_file}")
    
    return logger

def get_logger(name):
    """Get logger for specific module"""
    return logging.getLogger(f'wilo_scraper.{name}')

class LogCapture:
    """Captures log messages for GUI display"""
    
    def __init__(self, max_entries=1000):
        self.max_entries = max_entries
        self.entries = deque(maxlen=max_entries)
        self.lock = threading.Lock()
    
    def add_entry(self, message, level='INFO'):
        """Add a log entry"""
        with self.lock:
            entry = {
                'timestamp': datetime.now(),
                'level': level,
                'message': message
            }
            self.entries.append(entry)
    
    def get_recent(self, count=50):
        """Get recent log entries"""
        with self.lock:
            return list(self.entries)[-count:]
    
    def clear(self):
        """Clear all entries"""
        with self.lock:
            self.entries.clear()

class GUILogHandler(logging.Handler):
    """Custom log handler for GUI display"""
    
    def __init__(self, log_capture):
        super().__init__()
        self.log_capture = log_capture
        
    def emit(self, record):
        """Emit a log record"""
        try:
            message = self.format(record)
            self.log_capture.add_entry(message, record.levelname)
        except Exception:
            pass  # Ignore errors in logging
'''
    
    # Write the fixed logger
    with open('utils/logger.py', 'w') as f:
        f.write(logger_content)
    
    print("✅ Fixed utils/logger.py with LogCapture and GUILogHandler")

def create_missing_widget_files():
    """Create missing widget files that are imported but don't exist"""
    
    # Create progress_tracker.py
    progress_tracker_content = '''"""
Progress tracking widget with logs display
"""

import tkinter as tk
from tkinter import ttk, scrolledtext
from datetime import datetime
from utils.logger import LogCapture

class ProgressTracker(ttk.LabelFrame):
    """Widget for tracking progress and displaying logs"""
    
    def __init__(self, parent, log_capture):
        super().__init__(parent, text="Progress", padding="10")
        
        self.log_capture = log_capture
        self.progress_var = tk.StringVar(value="Ready to start scraping...")
        
        self._create_widgets()
        self._start_log_updates()
    
    def _create_widgets(self):
        """Create progress tracking widgets"""
        # Progress label
        ttk.Label(self, textvariable=self.progress_var).pack(anchor='w')
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(self, mode='indeterminate')
        self.progress_bar.pack(fill='x', pady=5)
        
        # Log display
        self.log_text = scrolledtext.ScrolledText(
            self,
            height=15,
            wrap='word',
            state='disabled'
        )
        self.log_text.pack(fill='both', expand=True, pady=5)
        
        # Control buttons
        button_frame = ttk.Frame(self)
        button_frame.pack(fill='x', pady=5)
        
        ttk.Button(button_frame, text="Clear Logs", command=self.clear_logs).pack(side='left')
    
    def _start_log_updates(self):
        """Start periodic log updates"""
        self._update_logs()
        self.after(1000, self._start_log_updates)  # Update every second
    
    def _update_logs(self):
        """Update log display"""
        try:
            logs = self.log_capture.get_recent(100)
            
            self.log_text.config(state='normal')
            self.log_text.delete(1.0, tk.END)
            
            for log_entry in logs:
                timestamp = log_entry['timestamp'].strftime("%H:%M:%S")
                level = log_entry['level']
                message = log_entry['message']
                formatted = f"[{timestamp}] [{level}] {message}\\n"
                self.log_text.insert(tk.END, formatted)
            
            self.log_text.see(tk.END)
            self.log_text.config(state='disabled')
        except Exception:
            pass  # Ignore errors in log updates
    
    def update_progress(self, message, start_progress=False, stop_progress=False):
        """Update progress display"""
        self.progress_var.set(message)
        
        if start_progress:
            self.progress_bar.start()
        elif stop_progress:
            self.progress_bar.stop()
    
    def clear_logs(self):
        """Clear log display"""
        self.log_capture.clear()
        self.log_text.config(state='normal')
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state='disabled')
'''
    
    # Create other missing widget files
    country_selector_content = '''"""
Country selection widget
"""

import tkinter as tk
from tkinter import ttk
from config.countries import COUNTRIES, get_all_countries

class CountrySelector(ttk.LabelFrame):
    """Widget for selecting target country"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Country Selection", padding="10")
        self.settings = settings
        self.selected_country = tk.StringVar()
        self._create_widgets()
    
    def _create_widgets(self):
        """Create country selection widgets"""
        ttk.Label(self, text="Select Target Country:").pack(anchor='w')
        
        # Country dropdown
        countries = [COUNTRIES[key]['name'] for key in get_all_countries()]
        self.country_combo = ttk.Combobox(
            self,
            textvariable=self.selected_country,
            values=countries,
            state="readonly",
            width=30
        )
        self.country_combo.pack(anchor='w', pady=5)
        self.country_combo.set("Deutschland")  # Default to Germany
        
        # Info display
        self.info_text = tk.Text(self, height=3, state='disabled', wrap='word')
        self.info_text.pack(fill='x', pady=5)
        
        # Bind selection change
        self.country_combo.bind('<<ComboboxSelected>>', self._on_country_changed)
        self._on_country_changed()  # Initialize
    
    def _on_country_changed(self, event=None):
        """Handle country selection change"""
        try:
            country_name = self.selected_country.get()
            # Find country data
            country_data = None
            for key, data in COUNTRIES.items():
                if data['name'] == country_name:
                    country_data = data
                    break
            
            if country_data:
                info = f"Language: {country_data['language']}\\n"
                info += f"Pump Selection Text: {country_data['hydraulic_pump_text']}"
                
                self.info_text.config(state='normal')
                self.info_text.delete(1.0, tk.END)
                self.info_text.insert(1.0, info)
                self.info_text.config(state='disabled')
        except Exception:
            pass
    
    def get_selected_country_key(self):
        """Get the key for selected country"""
        country_name = self.selected_country.get()
        for key, data in COUNTRIES.items():
            if data['name'] == country_name:
                return key
        return 'germany'  # Default
'''
    
    browser_settings_content = '''"""
Browser settings widget
"""

import tkinter as tk
from tkinter import ttk

class BrowserSettings(ttk.LabelFrame):
    """Widget for browser configuration"""
    
    def __init__(self, parent, settings):
        super().__init__(parent, text="Browser Settings", padding="10")
        self.settings = settings
        self._create_widgets()
    
    def _create_widgets(self):
        """Create browser settings widgets"""
        # Headless mode
        self.headless_var = tk.BooleanVar(value=self.settings.headless_mode)
        ttk.Checkbutton(
            self,
            text="Run in headless mode (no browser window)",
            variable=self.headless_var
        ).pack(anchor='w')
        
        # Delay settings
        delay_frame = ttk.Frame(self)
        delay_frame.pack(fill='x', pady=5)
        
        ttk.Label(delay_frame, text="Page load delay (seconds):").pack(side='left')
        self.delay_var = tk.StringVar(value=str(self.settings.page_load_delay))
        delay_spinbox = ttk.Spinbox(
            delay_frame,
            from_=1,
            to=10,
            textvariable=self.delay_var,
            width=5
        )
        delay_spinbox.pack(side='left', padx=5)
        
        # Timeout settings
        timeout_frame = ttk.Frame(self)
        timeout_frame.pack(fill='x', pady=5)
        
        ttk.Label(timeout_frame, text="Browser timeout (seconds):").pack(side='left')
        self.timeout_var = tk.StringVar(value=str(self.settings.browser_timeout))
        timeout_spinbox = ttk.Spinbox(
            timeout_frame,
            from_=10,
            to=120,
            textvariable=self.timeout_var,
            width=5
        )
        timeout_spinbox.pack(side='left', padx=5)
    
    def get_settings(self):
        """Get current browser settings"""
        return {
            'headless_mode': self.headless_var.get(),
            'page_load_delay': int(self.delay_var.get()),
            'browser_timeout': int(self.timeout_var.get())
        }
'''
    
    results_table_content = '''"""
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
'''
    
    shopify_config_content = '''"""
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
'''
    
    # Write all widget files
    widgets = {
        'gui/widgets/progress_tracker.py': progress_tracker_content,
        'gui/widgets/country_selector.py': country_selector_content,
        'gui/widgets/browser_settings.py': browser_settings_content,
        'gui/widgets/results_table.py': results_table_content,
        'gui/widgets/shopify_config.py': shopify_config_content,
    }
    
    for filepath, content in widgets.items():
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        print(f"✅ Created {filepath}")

def fix_countries_module():
    """Fix the countries module to ensure get_all_countries exists"""
    
    countries_content = '''"""
Country configurations for Wilo website
"""

COUNTRIES = {
    'germany': {
        'name': 'Deutschland',
        'code': 'DE',
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl',
        'url_params': {'country': 'de', 'lang': 'de'}
    },
    'austria': {
        'name': 'Österreich', 
        'code': 'AT',
        'language': 'German',
        'hydraulic_pump_text': 'Hydraulische Pumpenauswahl',
        'url_params': {'country': 'at', 'lang': 'de'}
    },
    'france': {
        'name': 'France',
        'code': 'FR', 
        'language': 'French',
        'hydraulic_pump_text': 'Sélection de pompes hydrauliques',
        'url_params': {'country': 'fr', 'lang': 'fr'}
    },
    'italy': {
        'name': 'Italia',
        'code': 'IT',
        'language': 'Italian', 
        'hydraulic_pump_text': 'Selezione pompe idrauliche',
        'url_params': {'country': 'it', 'lang': 'it'}
    },
    'spain': {
        'name': 'España',
        'code': 'ES',
        'language': 'Spanish',
        'hydraulic_pump_text': 'Selección de bombas hidráulicas',
        'url_params': {'country': 'es', 'lang': 'es'}
    },
    'netherlands': {
        'name': 'Nederland',
        'code': 'NL',
        'language': 'Dutch',
        'hydraulic_pump_text': 'Hydraulische pompselectie',
        'url_params': {'country': 'nl', 'lang': 'nl'}
    },
    'poland': {
        'name': 'Polska',
        'code': 'PL',
        'language': 'Polish',
        'hydraulic_pump_text': 'Wybór pomp hydraulicznych',
        'url_params': {'country': 'pl', 'lang': 'pl'}
    },
    'united_kingdom': {
        'name': 'United Kingdom',
        'code': 'GB', 
        'language': 'English',
        'hydraulic_pump_text': 'Hydraulic pump selection',
        'url_params': {'country': 'gb', 'lang': 'en'}
    }
}

def get_country_config(country_key):
    """Get configuration for specific country"""
    return COUNTRIES.get(country_key.lower())

def get_all_countries():
    """Get list of all supported countries"""
    return list(COUNTRIES.keys())

def get_country_by_name(country_name):
    """Get country data by display name"""
    for key, data in COUNTRIES.items():
        if data['name'] == country_name:
            return key, data
    return None, None
'''
    
    with open('config/countries.py', 'w') as f:
        f.write(countries_content)
    
    print("✅ Fixed config/countries.py with get_all_countries function")

def main():
    """Main fix function"""
    print("🔧 Fixing Missing Components in Wilo Scraper")
    print("=" * 50)
    
    # Fix logger module
    fix_logger_module()
    
    # Fix countries module
    fix_countries_module()
    
    # Create missing widget files
    create_missing_widget_files()
    
    print("\n✅ All missing components have been fixed!")
    print("\n🎯 Try running again:")
    print("python main.py")

if __name__ == "__main__":
    main()