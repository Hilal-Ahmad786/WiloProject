"""
Pump selection navigation logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
import time

class PumpNavigator:
    """Handles pump selection navigation"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def navigate_to_pump_selection(self, driver) -> bool:
        """Navigate to hydraulic pump selection"""
        try:
            self.logger.info("Navigating to pump selection...")
            wait = WebDriverWait(driver, 20)
            
            # Find the tile with "Hydraulische Pumpenauswahl"
            try:
                pump_element = wait.until(
                    EC.element_to_be_clickable((By.XPATH, 
                        "//span[contains(text(), 'Hydraulische Pumpenauswahl')]//ancestor::div[contains(@class, 'tileButton')]"
                    ))
                )
                
                driver.execute_script("arguments[0].scrollIntoView(true);", pump_element)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", pump_element)
                
                self.logger.info("Pump selection successful")
                time.sleep(self.settings.scraping.delay_between_actions)
                return True
                
            except Exception as e:
                self.logger.error(f"Failed to find pump selection tile: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False
