"""
Simple Browser Manager - Just Open Chrome
"""

import time
import subprocess
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from utils.logger import get_logger

class BrowserManager:
    """Super simple browser manager - just open Chrome"""
    
    def __init__(self, settings):
        self.settings = settings
        self.driver = None
        self.logger = get_logger(__name__)
        
    def setup_driver(self) -> bool:
        """Simple Chrome setup - no fancy stuff"""
        try:
            self.logger.info("Setting up Chrome browser (simple mode)...")
            
            # Simple Chrome options
            options = Options()
            
            # Only essential options
            if getattr(self.settings, 'headless_mode', False):
                options.add_argument('--headless')
                
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            options.add_argument('--window-size=1920,1080')
            
            # Try the simplest approach - let Selenium handle everything
            try:
                self.logger.info("Trying simple Chrome setup...")
                self.driver = webdriver.Chrome(options=options)
                
                # Quick test
                self.driver.get("data:text/html,<h1>Test</h1>")
                if "Test" in self.driver.page_source:
                    self.logger.info("✅ Chrome opened successfully!")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Simple setup failed: {e}")
                
                # Try with explicit service (empty)
                try:
                    self.logger.info("Trying with empty service...")
                    service = Service()
                    self.driver = webdriver.Chrome(service=service, options=options)
                    
                    self.driver.get("data:text/html,<h1>Test</h1>")
                    if "Test" in self.driver.page_source:
                        self.logger.info("✅ Chrome opened with service!")
                        return True
                        
                except Exception as e2:
                    self.logger.warning(f"Service setup failed: {e2}")
                    
                    # Last resort - try to find Chrome manually
                    try:
                        self.logger.info("Looking for Chrome manually...")
                        
                        # Check if Chrome is installed
                        chrome_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
                        if subprocess.run(["test", "-f", chrome_path], capture_output=True).returncode == 0:
                            options.binary_location = chrome_path
                            self.driver = webdriver.Chrome(options=options)
                            
                            self.driver.get("data:text/html,<h1>Test</h1>")
                            if "Test" in self.driver.page_source:
                                self.logger.info("✅ Chrome opened with manual path!")
                                return True
                        else:
                            self.logger.error("Chrome not found at expected location")
                            
                    except Exception as e3:
                        self.logger.error(f"Manual setup failed: {e3}")
            
            return False
            
        except Exception as e:
            self.logger.error(f"Browser setup completely failed: {e}")
            return False
    
    def get_driver(self):
        """Get the driver"""
        return self.driver
    
    def navigate_to(self, url: str) -> bool:
        """Navigate to URL"""
        try:
            if not self.driver:
                return False
                
            self.logger.info(f"Going to: {url}")
            self.driver.get(url)
            time.sleep(3)  # Simple wait
            return True
            
        except Exception as e:
            self.logger.error(f"Navigation failed: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot"""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
            
            import os
            os.makedirs("logs/screenshots", exist_ok=True)
            filepath = f"logs/screenshots/{filename}"
            
            if self.driver:
                self.driver.save_screenshot(filepath)
                self.logger.info(f"Screenshot: {filepath}")
                return filepath
                
        except Exception as e:
            self.logger.error(f"Screenshot failed: {e}")
            return ""
    
    def quit(self):
        """Close browser"""
        if self.driver:
            try:
                self.logger.info("Closing browser...")
                self.driver.quit()
                self.logger.info("✅ Browser closed")
            except:
                pass
            finally:
                self.driver = None
