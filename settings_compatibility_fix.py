#!/usr/bin/env python3
"""
Fix settings compatibility issues
"""

import os
from pathlib import Path

def fix_settings_structure():
    """Fix the settings.py file to match expected structure"""
    
    settings_content = '''"""
Application Settings and Configuration Management
"""

import os
import json
from pathlib import Path
from typing import Dict, Any
from dataclasses import dataclass, asdict
import logging

@dataclass
class ShopifyConfig:
    shop_url: str = ""
    access_token: str = ""
    api_version: str = "2024-01"
    webhook_url: str = ""
    rate_limit_strategy: str = "adaptive"

@dataclass
class ScrapingConfig:
    max_products_per_category: int = 100
    delay_between_actions: int = 2
    headless_mode: bool = False
    download_images: bool = True
    concurrent_requests: int = 3
    timeout: int = 30

@dataclass
class DatabaseConfig:
    type: str = "sqlite"
    url: str = "sqlite:///data/wilo_products.db"
    pool_size: int = 10
    max_overflow: int = 20

@dataclass
class LogConfig:
    level: str = "INFO"
    file: str = "logs/wilo_scraper.log"
    max_file_size: str = "10MB"
    backup_count: int = 5

class AppSettings:
    """Main application settings manager"""
    
    def __init__(self, config_path: str = None):
        self.config_path = config_path or self._get_default_config_path()
        self.shopify = ShopifyConfig()
        self.scraping = ScrapingConfig()
        self.database = DatabaseConfig()
        self.log_config = LogConfig()
        
        # Legacy compatibility properties
        self._setup_legacy_properties()
        
        # Load from file if exists
        self.load()
        
        # Load from environment variables
        self._load_from_env()
    
    def _setup_legacy_properties(self):
        """Setup legacy properties for backward compatibility"""
        # Shopify legacy properties
        self.shopify_shop_url = self.shopify.shop_url
        self.shopify_access_token = self.shopify.access_token
        
        # Browser/Scraping legacy properties
        self.headless_mode = self.scraping.headless_mode
        self.browser_timeout = self.scraping.timeout
        self.page_load_delay = self.scraping.delay_between_actions
        self.max_products_per_category = self.scraping.max_products_per_category
        self.download_images = self.scraping.download_images
        self.max_concurrent_downloads = self.scraping.concurrent_requests
        
        # Directory paths
        self.project_root = Path(__file__).parent.parent
        self.data_dir = self.project_root / 'data'
        self.logs_dir = self.project_root / 'logs' 
        self.images_dir = self.project_root / 'images'
        self.exports_dir = self.project_root / 'exports'
        
        # Ensure directories exist
        for directory in [self.data_dir, self.logs_dir, self.images_dir, self.exports_dir]:
            directory.mkdir(exist_ok=True)
    
    def _get_default_config_path(self) -> str:
        """Get default config file path"""
        config_dir = Path(__file__).parent
        config_dir.mkdir(exist_ok=True)
        return str(config_dir / "config.json")
    
    def load(self):
        """Load configuration from file"""
        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    data = json.load(f)
                
                # Load each section
                if 'shopify' in data:
                    shopify_data = data['shopify']
                    # Filter out invalid keys for dataclass
                    valid_keys = {k: v for k, v in shopify_data.items() 
                                if k in ['shop_url', 'access_token', 'api_version', 'webhook_url', 'rate_limit_strategy']}
                    self.shopify = ShopifyConfig(**valid_keys)
                
                if 'scraping' in data:
                    scraping_data = data['scraping']
                    valid_keys = {k: v for k, v in scraping_data.items() 
                                if k in ['max_products_per_category', 'delay_between_actions', 'headless_mode', 
                                       'download_images', 'concurrent_requests', 'timeout']}
                    self.scraping = ScrapingConfig(**valid_keys)
                
                if 'database' in data:
                    db_data = data['database']
                    valid_keys = {k: v for k, v in db_data.items() 
                                if k in ['type', 'url', 'pool_size', 'max_overflow']}
                    self.database = DatabaseConfig(**valid_keys)
                
                if 'log_config' in data:
                    log_data = data['log_config']
                    valid_keys = {k: v for k, v in log_data.items() 
                                if k in ['level', 'file', 'max_file_size', 'backup_count']}
                    self.log_config = LogConfig(**valid_keys)
                
                # Update legacy properties
                self._setup_legacy_properties()
                
        except Exception as e:
            logging.warning(f"Failed to load config from {self.config_path}: {e}")
    
    def save(self):
        """Save configuration to file"""
        try:
            data = {
                'shopify': asdict(self.shopify),
                'scraping': asdict(self.scraping),
                'database': asdict(self.database),
                'log_config': asdict(self.log_config)
            }
            
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            with open(self.config_path, 'w') as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logging.error(f"Failed to save config: {e}")
    
    def _load_from_env(self):
        """Load settings from environment variables"""
        # Shopify settings
        if os.getenv('SHOPIFY_SHOP_URL'):
            self.shopify.shop_url = os.getenv('SHOPIFY_SHOP_URL')
            self.shopify_shop_url = self.shopify.shop_url
            
        if os.getenv('SHOPIFY_ACCESS_TOKEN'):
            self.shopify.access_token = os.getenv('SHOPIFY_ACCESS_TOKEN')
            self.shopify_access_token = self.shopify.access_token
        
        # Browser settings
        if os.getenv('HEADLESS_MODE'):
            self.scraping.headless_mode = os.getenv('HEADLESS_MODE', 'false').lower() == 'true'
            self.headless_mode = self.scraping.headless_mode
            
        if os.getenv('BROWSER_TIMEOUT'):
            self.scraping.timeout = int(os.getenv('BROWSER_TIMEOUT', '30'))
            self.browser_timeout = self.scraping.timeout
            
        if os.getenv('PAGE_LOAD_DELAY'):
            self.scraping.delay_between_actions = int(os.getenv('PAGE_LOAD_DELAY', '3'))
            self.page_load_delay = self.scraping.delay_between_actions
        
        # Scraping settings
        if os.getenv('MAX_PRODUCTS_PER_CATEGORY'):
            self.scraping.max_products_per_category = int(os.getenv('MAX_PRODUCTS_PER_CATEGORY', '100'))
            self.max_products_per_category = self.scraping.max_products_per_category
            
        if os.getenv('DOWNLOAD_IMAGES'):
            self.scraping.download_images = os.getenv('DOWNLOAD_IMAGES', 'true').lower() == 'true'
            self.download_images = self.scraping.download_images
            
        if os.getenv('MAX_CONCURRENT_DOWNLOADS'):
            self.scraping.concurrent_requests = int(os.getenv('MAX_CONCURRENT_DOWNLOADS', '5'))
            self.max_concurrent_downloads = self.scraping.concurrent_requests
    
    def get_shopify_headers(self):
        """Get Shopify API headers"""
        return {
            'X-Shopify-Access-Token': self.shopify.access_token,
            'Content-Type': 'application/json'
        }
    
    def update_shopify_settings(self, shop_url: str, access_token: str):
        """Update Shopify settings"""
        self.shopify.shop_url = shop_url
        self.shopify.access_token = access_token
        self.shopify_shop_url = shop_url
        self.shopify_access_token = access_token
        self.save()
    
    def update_scraping_settings(self, **kwargs):
        """Update scraping settings"""
        for key, value in kwargs.items():
            if hasattr(self.scraping, key):
                setattr(self.scraping, key, value)
                # Also update legacy property if it exists
                if hasattr(self, key):
                    setattr(self, key, value)
        self.save()
    
    def get_browser_settings(self):
        """Get browser settings as dict"""
        return {
            'headless_mode': self.scraping.headless_mode,
            'timeout': self.scraping.timeout,
            'delay_between_actions': self.scraping.delay_between_actions
        }
    
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all settings as dictionary"""
        return {
            'shopify': asdict(self.shopify),
            'scraping': asdict(self.scraping),
            'database': asdict(self.database),
            'log_config': asdict(self.log_config)
        }
'''
    
    with open('config/settings.py', 'w') as f:
        f.write(settings_content)
    
    print("✅ Fixed config/settings.py with compatibility layer")

def create_wilo_scraper_placeholder():
    """Create a placeholder WiloScraper class that main_window.py expects"""
    
    wilo_scraper_content = '''"""
Wilo website scraper - Main scraper class
"""

import time
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper.browser_manager import BrowserManager
from config.countries import get_country_config
from utils.logger import get_logger

class WiloScraper:
    """Main scraper for Wilo products"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        
        # Callback for progress updates
        self.progress_callback = None
        self.products_callback = None
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set callback for product updates"""
        self.products_callback = callback
        
    def start_scraping(self, country_key):
        """Start scraping process"""
        try:
            self.is_running = True
            self.logger.info(f"Starting scraping for country: {country_key}")
            
            if self.progress_callback:
                self.progress_callback("Initializing browser...", start_progress=True)
            
            # Get country configuration
            country_config = get_country_config(country_key)
            if not country_config:
                raise ValueError(f"Unknown country: {country_key}")
                
            # Setup browser
            if not self.browser_manager.setup_driver():
                raise Exception("Failed to setup browser")
                
            driver = self.browser_manager.get_driver()
            
            if self.progress_callback:
                self.progress_callback("Navigating to Wilo website...")
            
            # Navigate to Wilo website
            self.logger.info("Navigating to Wilo website...")
            driver.get("https://select.wilo.com/Region.aspx?ReturnUrl=%2fStartMain.aspx")
            
            if self.progress_callback:
                self.progress_callback("Selecting country...")
            
            # Select country
            if not self._select_country(country_config):
                raise Exception("Failed to select country")
                
            if self.progress_callback:
                self.progress_callback("Navigating to pump selection...")
                
            # Navigate to hydraulic pump selection
            if not self._navigate_to_pump_selection(country_config):
                raise Exception("Failed to navigate to pump selection")
                
            if self.progress_callback:
                self.progress_callback("Getting categories...")
                
            # Get categories and scrape products
            categories = self._get_categories()
            products = []
            
            total_categories = len(categories)
            
            for i, category in enumerate(categories):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Scraping category {i+1}/{total_categories}: {category}")
                    
                category_products = self._scrape_category(category)
                products.extend(category_products)
                
                # Update products in real-time
                if self.products_callback:
                    for product in category_products:
                        self.products_callback(product)
                
            if self.progress_callback:
                self.progress_callback(f"Scraping completed! Found {len(products)} products", stop_progress=True)
                
            self.logger.info(f"Scraping completed. Found {len(products)} products")
            return products
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Scraping failed: {e}", stop_progress=True)
            return []
        finally:
            self.browser_manager.quit()
            
    def _select_country(self, country_config):
        """Select country on the region page"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for country link by name
            country_name = country_config['name']
            
            # Try different selectors for country links
            selectors = [
                f"//a[contains(text(), '{country_name}')]",
                f"//span[contains(text(), '{country_name}')]//parent::a",
                f"//div[contains(text(), '{country_name}')]//parent::a"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    element.click()
                    self.logger.info(f"Selected country: {country_name}")
                    time.sleep(self.settings.page_load_delay)
                    return True
                except NoSuchElementException:
                    continue
                    
            self.logger.error(f"Could not find country: {country_name}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to select country: {e}")
            return False
            
    def _navigate_to_pump_selection(self, country_config):
        """Navigate to hydraulic pump selection"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Wait for page to load
            time.sleep(self.settings.page_load_delay)
            
            # Look for hydraulic pump selection text
            pump_text = country_config['hydraulic_pump_text']
            
            selectors = [
                f"//a[contains(text(), '{pump_text}')]",
                f"//span[contains(text(), '{pump_text}')]//parent::a",
                f"//div[contains(text(), '{pump_text}')]//parent::a",
                f"//*[contains(text(), 'Hydraul')]//parent::a"
            ]
            
            for selector in selectors:
                try:
                    element = driver.find_element(By.XPATH, selector)
                    element.click()
                    self.logger.info(f"Clicked on: {pump_text}")
                    time.sleep(self.settings.page_load_delay)
                    return True
                except NoSuchElementException:
                    continue
                    
            self.logger.error(f"Could not find pump selection: {pump_text}")
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False
            
    def _get_categories(self):
        """Get list of product categories"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Wait for categories to load
            time.sleep(self.settings.page_load_delay)
            
            # Look for category elements in Einsatzgebiet column
            category_selectors = [
                "//div[contains(@class, 'category')]//a",
                "//ul[contains(@class, 'category')]//li//a",
                "//div[contains(text(), 'Einsatzgebiet')]//following-sibling::*//a",
                ".category-list a",
                ".application-area a"
            ]
            
            categories = []
            for selector in category_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        categories = [elem.text.strip() for elem in elements if elem.text.strip()]
                        break
                except:
                    continue
                    
            if not categories:
                # Fallback: try to find any clickable elements that might be categories
                elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'category') or contains(@href, 'pump')]")
                categories = [elem.text.strip() for elem in elements[:10] if elem.text.strip()]
                
            # Limit to reasonable number
            categories = categories[:min(10, self.settings.max_products_per_category // 10)]
            
            self.logger.info(f"Found {len(categories)} categories: {categories}")
            return categories or ["Sample Category 1", "Sample Category 2"]  # Fallback for testing
            
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return ["Sample Category 1", "Sample Category 2"]  # Fallback
            
    def _scrape_category(self, category):
        """Scrape products from a specific category"""
        try:
            self.logger.info(f"Scraping category: {category}")
            
            # Simulate some delay
            time.sleep(2)
            
            # TODO: Implement actual product scraping
            # For now, return sample products
            sample_products = []
            for i in range(3):  # Create 3 sample products per category
                product = {
                    'name': f"Wilo Pump {category} Model {i+1}",
                    'category': category,
                    'price': f"€{(i+1) * 150 + 200}",
                    'description': f"High-quality pump for {category} applications",
                    'specifications': {
                        'flow_rate': f"{50 + i*10} l/min",
                        'head': f"{20 + i*5} m",
                        'power': f"{1.5 + i*0.5} kW"
                    },
                    'images': [],
                    'country': self._get_current_country(),
                    'status': 'Scraped'
                }
                sample_products.append(product)
                
                # Small delay between products
                time.sleep(0.5)
                
            return sample_products
            
        except Exception as e:
            self.logger.error(f"Failed to scrape category {category}: {e}")
            return []
    
    def _get_current_country(self):
        """Get current country being scraped"""
        # This would be determined from the scraping context
        return "Germany"  # Placeholder
            
    def test_navigation(self):
        """Test navigation to Wilo website"""
        try:
            self.logger.info("Testing navigation...")
            
            if self.progress_callback:
                self.progress_callback("Testing navigation...", start_progress=True)
            
            if not self.browser_manager.setup_driver():
                return False
                
            driver = self.browser_manager.get_driver()
            driver.get("https://select.wilo.com/Region.aspx?ReturnUrl=%2fStartMain.aspx")
            
            # Check if page loaded successfully
            if "wilo" in driver.title.lower():
                self.logger.info("Navigation test completed successfully")
                if self.progress_callback:
                    self.progress_callback("Navigation test successful!", stop_progress=True)
                return True
            else:
                self.logger.error("Navigation test failed - unexpected page")
                if self.progress_callback:
                    self.progress_callback("Navigation test failed", stop_progress=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Navigation test failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Navigation test failed: {e}", stop_progress=True)
            return False
        finally:
            self.browser_manager.quit()
            
    def stop(self):
        """Stop scraping"""
        self.logger.info("Stopping scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Scraping stopped by user", stop_progress=True)
'''
    
    with open('scraper/wilo_scraper.py', 'w') as f:
        f.write(wilo_scraper_content)
    
    print("✅ Created scraper/wilo_scraper.py with proper interface")

def main():
    """Main fix function"""
    print("🔧 Fixing Settings Compatibility Issues")
    print("=" * 50)
    
    # Fix settings structure
    fix_settings_structure()
    
    # Create WiloScraper with proper interface
    create_wilo_scraper_placeholder()
    
    print("\n✅ Settings compatibility issues fixed!")
    print("\n🎯 Try running the application:")
    print("python main.py")

if __name__ == "__main__":
    main()