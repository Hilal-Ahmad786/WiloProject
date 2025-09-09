#!/usr/bin/env python3
"""
Fix browser setup for macOS compatibility issues
"""

def fix_browser_manager():
    """Fix browser manager with better macOS compatibility"""
    
    browser_manager_content = '''"""
Browser and WebDriver management for Wilo scraper - macOS Compatible
"""

import time
import os
import stat
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from typing import Optional
from utils.logger import get_logger

class BrowserManager:
    """Manages Chrome browser and WebDriver instances with macOS compatibility"""
    
    def __init__(self, settings):
        self.settings = settings
        self.driver: Optional[webdriver.Chrome] = None
        self.logger = get_logger(__name__)
        
    def setup_driver(self) -> bool:
        """Setup Chrome WebDriver with macOS compatibility fixes"""
        try:
            self.logger.info("Setting up Chrome browser...")
            
            chrome_options = self._get_chrome_options()
            
            # Try multiple ChromeDriver setup methods
            service = None
            
            # Method 1: Use webdriver-manager with fixed permissions
            try:
                self.logger.info("Attempting webdriver-manager setup...")
                chrome_driver_path = ChromeDriverManager().install()
                
                # Fix permissions on macOS
                if os.path.exists(chrome_driver_path):
                    os.chmod(chrome_driver_path, stat.S_IRWXU | stat.S_IRGRP | stat.S_IXGRP | stat.S_IROTH | stat.S_IXOTH)
                    self.logger.info(f"Fixed permissions for: {chrome_driver_path}")
                
                service = Service(chrome_driver_path)
                self.logger.info("webdriver-manager setup successful")
                
            except Exception as e:
                self.logger.warning(f"webdriver-manager failed: {e}")
                
                # Method 2: Try system Chrome installation
                try:
                    self.logger.info("Trying system ChromeDriver...")
                    # Common ChromeDriver locations on macOS
                    system_paths = [
                        "/usr/local/bin/chromedriver",
                        "/opt/homebrew/bin/chromedriver",
                        "/usr/bin/chromedriver"
                    ]
                    
                    for path in system_paths:
                        if os.path.exists(path) and os.access(path, os.X_OK):
                            service = Service(path)
                            self.logger.info(f"Using system ChromeDriver: {path}")
                            break
                            
                except Exception as e2:
                    self.logger.warning(f"System ChromeDriver failed: {e2}")
                    
                # Method 3: Try without explicit service (let Selenium handle it)
                if service is None:
                    self.logger.info("Trying default Selenium ChromeDriver handling...")
                    service = Service()  # Let Selenium find ChromeDriver
            
            # Create the driver with retries
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    self.logger.info(f"Creating Chrome driver (attempt {attempt + 1}/{max_retries})...")
                    
                    self.driver = webdriver.Chrome(service=service, options=chrome_options)
                    
                    # Set timeouts
                    self.driver.set_page_load_timeout(self.settings.browser_timeout)
                    self.driver.implicitly_wait(10)
                    
                    # Test basic functionality
                    self.logger.info("Testing browser functionality...")
                    self.driver.get("data:text/html,<html><body><h1>Test</h1></body></html>")
                    
                    if "Test" in self.driver.page_source:
                        self.logger.info("Browser setup successful!")
                        return True
                    else:
                        raise Exception("Browser test failed")
                        
                except Exception as e:
                    self.logger.warning(f"Driver creation attempt {attempt + 1} failed: {e}")
                    if self.driver:
                        try:
                            self.driver.quit()
                        except:
                            pass
                        self.driver = None
                    
                    if attempt < max_retries - 1:
                        time.sleep(2)  # Wait before retry
                    else:
                        raise e
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to setup driver: {e}")
            if self.driver:
                try:
                    self.driver.quit()
                except:
                    pass
                self.driver = None
            return False
    
    def _get_chrome_options(self) -> Options:
        """Get Chrome options optimized for macOS"""
        options = Options()
        
        # Headless mode
        if getattr(self.settings, 'headless_mode', False):
            options.add_argument('--headless=new')
            self.logger.info("Running in headless mode")
        
        # Essential options for macOS stability
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--disable-web-security')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-background-timer-throttling')
        options.add_argument('--disable-backgrounding-occluded-windows')
        options.add_argument('--disable-renderer-backgrounding')
        
        # macOS specific fixes
        options.add_argument('--disable-ipc-flooding-protection')
        options.add_argument('--disable-hang-monitor')
        options.add_argument('--disable-prompt-on-repost')
        options.add_argument('--disable-background-networking')
        
        # Window and display settings
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--start-maximized')
        
        # User agent
        options.add_argument('--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        # Performance options
        options.add_argument('--disable-extensions')
        options.add_argument('--disable-plugins')
        options.add_argument('--disable-default-apps')
        options.add_argument('--disable-sync')
        
        # Memory and process management
        options.add_argument('--memory-pressure-off')
        options.add_argument('--max_old_space_size=4096')
        
        # Anti-detection (minimal to avoid conflicts)
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        
        # Disable notifications and popups
        prefs = {
            "profile.default_content_setting_values.notifications": 2,
            "profile.default_content_settings.popups": 0,
            "profile.managed_default_content_settings.images": 1  # Allow images
        }
        options.add_experimental_option("prefs", prefs)
        
        # Logging
        options.add_argument('--log-level=3')  # Suppress INFO messages
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        options.add_experimental_option('useAutomationExtension', False)
        
        return options
    
    def get_driver(self) -> Optional[webdriver.Chrome]:
        """Get the current driver instance"""
        if self.driver is None:
            self.logger.warning("Driver not initialized. Call setup_driver() first.")
            return None
        return self.driver
    
    def is_driver_alive(self) -> bool:
        """Check if driver is still alive"""
        if self.driver is None:
            return False
        
        try:
            # Try to get current url to check if driver is responsive
            self.driver.current_url
            return True
        except:
            return False
    
    def restart_driver(self) -> bool:
        """Restart the driver"""
        self.logger.info("Restarting browser...")
        self.quit()
        return self.setup_driver()
    
    def navigate_to(self, url: str, max_retries: int = 3) -> bool:
        """Navigate to URL with retry logic"""
        for attempt in range(max_retries):
            try:
                if not self.is_driver_alive():
                    self.logger.warning("Driver not alive, restarting...")
                    if not self.restart_driver():
                        return False
                
                self.logger.info(f"Navigating to: {url}")
                self.driver.get(url)
                
                # Wait for page to load
                time.sleep(getattr(self.settings, 'page_load_delay', 3))
                
                # Check if page loaded successfully
                current_url = self.driver.current_url
                if current_url and current_url.startswith('http'):
                    self.logger.info(f"Successfully navigated to: {current_url}")
                    return True
                    
            except Exception as e:
                self.logger.warning(f"Navigation attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    self.logger.error(f"Failed to navigate to {url} after {max_retries} attempts")
                    return False
                
                # Wait before retry
                time.sleep(2)
        
        return False
    
    def wait_for_element(self, by, value, timeout=10):
        """Wait for element to be present"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(EC.presence_of_element_located((by, value)))
        except Exception as e:
            self.logger.error(f"Element not found: {by}={value}, error: {e}")
            return None
    
    def click_element(self, by, value, timeout=10):
        """Click element when clickable"""
        try:
            from selenium.webdriver.support.ui import WebDriverWait
            from selenium.webdriver.support import expected_conditions as EC
            
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.element_to_be_clickable((by, value)))
            element.click()
            return True
        except Exception as e:
            self.logger.error(f"Failed to click element: {by}={value}, error: {e}")
            return False
    
    def take_screenshot(self, filename: str = None) -> str:
        """Take screenshot and save to file"""
        try:
            if not filename:
                from datetime import datetime
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                filename = f"screenshot_{timestamp}.png"
            
            # Ensure screenshots directory exists
            import os
            screenshot_dir = "logs/screenshots"
            os.makedirs(screenshot_dir, exist_ok=True)
            
            filepath = os.path.join(screenshot_dir, filename)
            
            if self.driver:
                self.driver.save_screenshot(filepath)
                self.logger.info(f"Screenshot saved: {filepath}")
                return filepath
            else:
                self.logger.error("No driver available for screenshot")
                return ""
                
        except Exception as e:
            self.logger.error(f"Failed to take screenshot: {e}")
            return ""
    
    def get_page_source(self) -> str:
        """Get current page source"""
        try:
            if self.driver:
                return self.driver.page_source
            return ""
        except Exception as e:
            self.logger.error(f"Failed to get page source: {e}")
            return ""
    
    def execute_script(self, script: str, *args):
        """Execute JavaScript in the browser"""
        try:
            if self.driver:
                return self.driver.execute_script(script, *args)
            return None
        except Exception as e:
            self.logger.error(f"Failed to execute script: {e}")
            return None
    
    def quit(self):
        """Quit the browser and clean up"""
        if self.driver:
            try:
                self.logger.info("Closing browser...")
                self.driver.quit()
            except Exception as e:
                self.logger.warning(f"Error during driver quit: {e}")
            finally:
                self.driver = None
                self.logger.info("Browser closed successfully")
    
    def __del__(self):
        """Cleanup on object destruction"""
        self.quit()
    
    def __enter__(self):
        """Context manager entry"""
        self.setup_driver()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.quit()
'''
    
    with open('scraper/browser_manager.py', 'w') as f:
        f.write(browser_manager_content)
    
    print("✅ Fixed scraper/browser_manager.py with macOS compatibility improvements")

def install_chrome_dependencies():
    """Provide instructions for installing Chrome dependencies"""
    
    instructions = '''
🔧 macOS Chrome Setup Instructions
==================================

If you're still having issues, try these steps:

1. **Install Homebrew** (if not already installed):
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

2. **Install ChromeDriver via Homebrew**:
   brew install chromedriver

3. **Fix ChromeDriver permissions**:
   xattr -d com.apple.quarantine $(which chromedriver)
   chmod +x $(which chromedriver)

4. **Verify Chrome installation**:
   /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome --version

5. **Alternative: Install Chrome via Homebrew**:
   brew install --cask google-chrome

6. **If still having issues, try manual ChromeDriver**:
   - Download from: https://chromedriver.chromium.org/
   - Place in /usr/local/bin/
   - Run: chmod +x /usr/local/bin/chromedriver
   - Run: xattr -d com.apple.quarantine /usr/local/bin/chromedriver

🎯 After running these commands, try the application again!
'''
    
    print(instructions)

def main():
    """Main fix function"""
    print("🔧 Fixing Browser Compatibility for macOS")
    print("=" * 45)
    
    # Fix browser manager
    fix_browser_manager()
    
    # Show additional setup instructions
    install_chrome_dependencies()
    
    print("\n✅ Browser compatibility fixes applied!")
    print("\n🎯 Try running the application:")
    print("python main.py")

if __name__ == "__main__":
    main()