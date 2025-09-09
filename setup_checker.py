#!/usr/bin/env python3
"""
Wilo Scraper Project Setup Checker
Creates all missing files and validates the project structure
"""

import os
import sys
from pathlib import Path

class ProjectSetupChecker:
    def __init__(self):
        self.project_root = Path.cwd()
        self.issues = []
        self.created_files = []
        
    def check_and_create_all(self):
        """Main function to check and create everything"""
        print("Checking Wilo Scraper Project Setup...")
        print("=" * 60)
        
        # Check directory structure
        self.check_directories()
        
        # Create missing files
        self.create_missing_files()
        
        # Validate imports
        self.validate_imports()
        
        # Report results
        self.report_results()
    
    def check_directories(self):
        """Check and create required directories"""
        required_dirs = [
            "config", "gui", "gui/widgets", "gui/dialogs",
            "scraper", "scraper/navigation", "scraper/extractors", 
            "shopify", "utils", "data", "logs", "logs/screenshots"
        ]
        
        print("Checking directories...")
        for directory in required_dirs:
            dir_path = self.project_root / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                self.created_files.append(f"Directory: {directory}")
                print(f"  ✅ Created: {directory}/")
            else:
                print(f"  ✓ Exists: {directory}/")
    
    def create_missing_files(self):
        """Create all missing module files"""
        print("\nCreating missing files...")
        
        # Core files
        self.create_main_py()
        self.create_config_files()
        self.create_utils_files()
        self.create_gui_files()
        self.create_scraper_files()
        self.create_shopify_files()
        self.create_init_files()
    
    def create_main_py(self):
        """Create main.py entry point"""
        main_content = '''#!/usr/bin/env python3
"""
Wilo Product Scraper - Main Entry Point
"""

import sys
import os
import tkinter as tk
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import AppSettings
from utils.logger import setup_logging, get_logger
from gui.main_window import MainWindow

def main():
    """Main application entry point"""
    try:
        # Setup logging
        setup_logging()
        logger = get_logger(__name__)
        
        logger.info("Starting Wilo Scraper Application")
        
        # Load settings
        settings = AppSettings()
        
        # Create GUI
        root = tk.Tk()
        app = MainWindow(root, settings)
        
        # Start application
        root.mainloop()
        
    except Exception as e:
        print(f"Error starting application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
        self._write_file("main.py", main_content)
        
    def create_config_files(self):
        """Create configuration files"""
        
        # settings.py
        settings_content = '''"""
Application settings and configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class AppSettings:
    """Application settings"""
    
    def __init__(self):
        self.project_root = Path(__file__).parent.parent
        self.load_settings()
    
    def load_settings(self):
        """Load settings from environment"""
        
        # Shopify settings
        self.shopify_shop_url = os.getenv('SHOPIFY_SHOP_URL', '')
        self.shopify_access_token = os.getenv('SHOPIFY_ACCESS_TOKEN', '')
        
        # Browser settings
        self.headless_mode = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
        self.browser_timeout = int(os.getenv('BROWSER_TIMEOUT', '30'))
        self.page_load_delay = int(os.getenv('PAGE_LOAD_DELAY', '3'))
        
        # Scraping settings
        self.max_products_per_category = int(os.getenv('MAX_PRODUCTS_PER_CATEGORY', '100'))
        self.download_images = os.getenv('DOWNLOAD_IMAGES', 'true').lower() == 'true'
        self.max_concurrent_downloads = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', '5'))
        
        # File paths
        self.data_dir = self.project_root / 'data'
        self.logs_dir = self.project_root / 'logs' 
        self.images_dir = self.project_root / 'images'
        self.exports_dir = self.project_root / 'exports'
        
        # Ensure directories exist
        for directory in [self.data_dir, self.logs_dir, self.images_dir, self.exports_dir]:
            directory.mkdir(exist_ok=True)
    
    def get_shopify_headers(self):
        """Get Shopify API headers"""
        return {
            'X-Shopify-Access-Token': self.shopify_access_token,
            'Content-Type': 'application/json'
        }
'''
        self._write_file("config/settings.py", settings_content)
        
        # countries.py
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
    }
}

def get_country_config(country_key):
    """Get configuration for specific country"""
    return COUNTRIES.get(country_key.lower())

def get_all_countries():
    """Get list of all supported countries"""
    return list(COUNTRIES.keys())
'''
        self._write_file("config/countries.py", countries_content)
        
    def create_utils_files(self):
        """Create utility files"""
        
        # logger.py
        logger_content = '''"""
Logging utilities
"""

import logging
import sys
from pathlib import Path
from datetime import datetime

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
'''
        self._write_file("utils/logger.py", logger_content)
        
    def create_gui_files(self):
        """Create GUI module files"""
        
        # main_window.py
        main_window_content = '''"""
Main application window
"""

import tkinter as tk
from tkinter import ttk
from utils.logger import get_logger
from gui.widgets.scraper_tab import ScraperTab
from gui.widgets.config_tab import ConfigTab
from gui.widgets.results_tab import ResultsTab

class MainWindow:
    """Main application window"""
    
    def __init__(self, root, settings):
        self.root = root
        self.settings = settings
        self.logger = get_logger(__name__)
        
        self.setup_window()
        self.create_widgets()
        
    def setup_window(self):
        """Setup main window"""
        self.root.title("Wilo Product Scraper & Shopify Uploader")
        self.root.geometry("1200x800")
        
    def create_widgets(self):
        """Create main widgets"""
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create tabs
        self.scraper_tab = ScraperTab(self.notebook, self.settings)
        self.config_tab = ConfigTab(self.notebook, self.settings)
        self.results_tab = ResultsTab(self.notebook, self.settings)
        
        # Add tabs to notebook
        self.notebook.add(self.scraper_tab.frame, text="Main Scraper")
        self.notebook.add(self.config_tab.frame, text="Configuration") 
        self.notebook.add(self.results_tab.frame, text="Results")
'''
        self._write_file("gui/main_window.py", main_window_content)
        
        # scraper_tab.py
        scraper_tab_content = '''"""
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
'''
        self._write_file("gui/widgets/scraper_tab.py", scraper_tab_content)
        
        # config_tab.py  
        config_tab_content = '''"""
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
'''
        self._write_file("gui/widgets/config_tab.py", config_tab_content)
        
        # results_tab.py
        results_tab_content = '''"""
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
'''
        self._write_file("gui/widgets/results_tab.py", results_tab_content)
        
    def create_scraper_files(self):
        """Create scraper module files"""
        
        # browser_manager.py
        browser_manager_content = '''"""
Browser management for web scraping
"""

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from utils.logger import get_logger

class BrowserManager:
    """Manages browser instances for scraping"""
    
    def __init__(self, settings):
        self.settings = settings
        self.driver = None
        self.logger = get_logger(__name__)
        
    def setup_driver(self):
        """Setup Chrome driver with options"""
        try:
            self.logger.info("Setting up Chrome driver...")
            
            # Chrome options
            chrome_options = Options()
            
            if self.settings.headless_mode:
                chrome_options.add_argument("--headless")
                
            # Additional options for stability
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--disable-gpu")
            
            # Use webdriver-manager to handle ChromeDriver
            service = Service(ChromeDriverManager().install())
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(self.settings.browser_timeout)
            
            self.logger.info("Chrome driver setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {e}")
            return False
            
    def get_driver(self):
        """Get driver instance"""
        return self.driver
            
    def quit(self):
        """Quit browser"""
        if self.driver:
            try:
                self.driver.quit()
                self.logger.info("Browser closed")
            except Exception as e:
                self.logger.error(f"Error closing browser: {e}")
'''
        self._write_file("scraper/browser_manager.py", browser_manager_content)
        
    def create_shopify_files(self):
        """Create Shopify integration files"""
        
        # shopify_client.py
        shopify_client_content = '''"""
Shopify API client
"""

import requests
from utils.logger import get_logger

class ShopifyClient:
    """Shopify API client"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
        self.base_url = f"https://{settings.shopify_shop_url}/admin/api/2023-10"
        
    def test_connection(self):
        """Test Shopify API connection"""
        try:
            url = f"{self.base_url}/shop.json"
            headers = self.settings.get_shopify_headers()
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                shop_data = response.json()
                self.logger.info(f"Connected to shop: {shop_data['shop']['name']}")
                return True
            else:
                self.logger.error(f"Connection failed: {response.status_code}")
                return False
                
        except Exception as e:
            self.logger.error(f"Connection test failed: {e}")
            return False
'''
        self._write_file("shopify/shopify_client.py", shopify_client_content)
        
    def create_init_files(self):
        """Create __init__.py files for packages"""
        
        init_files = [
            "config/__init__.py",
            "gui/__init__.py", 
            "gui/widgets/__init__.py",
            "gui/dialogs/__init__.py",
            "scraper/__init__.py",
            "scraper/navigation/__init__.py",
            "scraper/extractors/__init__.py",
            "shopify/__init__.py",
            "utils/__init__.py"
        ]
        
        for init_file in init_files:
            self._write_file(init_file, "# Package initialization\n")
            
    def validate_imports(self):
        """Validate that all modules can be imported"""
        print("\nValidating imports...")
        
        test_imports = [
            "config.settings",
            "config.countries", 
            "utils.logger",
            "gui.main_window",
            "gui.widgets.scraper_tab",
            "gui.widgets.config_tab",
            "gui.widgets.results_tab",
            "scraper.browser_manager",
            "shopify.shopify_client"
        ]
        
        for module_name in test_imports:
            try:
                __import__(module_name)
                print(f"  ✓ {module_name}")
            except Exception as e:
                print(f"  ✗ {module_name}: {e}")
                self.issues.append(f"Import failed: {module_name} - {e}")
                
    def report_results(self):
        """Report setup results"""
        print("\n" + "="*60)
        print("SETUP REPORT")
        print("="*60)
        
        if self.created_files:
            print(f"✅ Created {len(self.created_files)} files/directories")
                
        if self.issues:
            print(f"\n⚠️  Issues found ({len(self.issues)}):")
            for issue in self.issues:
                print(f"   {issue}")
        else:
            print("\n✅ No issues found!")
            
        print(f"\n🎯 NEXT STEPS:")
        print("1. Run: python main.py")
        print("2. Test the GUI application")
        
        if not self.issues:
            print("\n🎉 PROJECT SETUP COMPLETE!")
    
    def _write_file(self, filepath, content):
        """Write file and track creation"""
        file_path = self.project_root / filepath
        
        if not file_path.exists():
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content)
            self.created_files.append(f"File: {filepath}")
            print(f"  ✅ Created: {filepath}")
        else:
            print(f"  ✓ Exists: {filepath}")

def main():
    """Main setup checker function"""
    print("🔧 Wilo Scraper Project Setup Checker")
    print("=" * 60)
    
    checker = ProjectSetupChecker()
    checker.check_and_create_all()
    
    return 0 if not checker.issues else 1

if __name__ == "__main__":
    exit(main())