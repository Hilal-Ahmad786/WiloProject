"""
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
