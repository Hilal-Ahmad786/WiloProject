"""
Country selection navigation logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import time

class CountryNavigator:
    """Handles country selection navigation"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def select_country(self, driver, country: str) -> bool:
        """Select a country from the list"""
        try:
            self.logger.info(f"Selecting country: {country}")
            wait = WebDriverWait(driver, 20)
            
            # Strategy 1: Find button by value attribute
            try:
                country_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[@value='{country}']"))
                )
                driver.execute_script("arguments[0].click();", country_button)
                self.logger.info("Country selected via button value")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
            except:
                pass
            
            # Strategy 2: Find button by text content  
            try:
                country_button = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//button[contains(.//span, '{country}')]"))
                )
                driver.execute_script("arguments[0].click();", country_button)
                self.logger.info("Country selected via button text")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            self.logger.error(f"Failed to select country {country}: {e}")
            return False
