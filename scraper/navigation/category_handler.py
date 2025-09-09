"""
Category handling logic
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.logger import get_logger
from typing import List, Dict
import time

class CategoryHandler:
    """Handles category detection and selection"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def get_categories(self, driver) -> List[Dict]:
        """Get available categories"""
        try:
            categories = []
            
            # Try dropdown approach
            try:
                category_elements = driver.find_elements(By.XPATH, "//ul[@class='rcbList']//li")
                for elem in category_elements:
                    text = elem.text.strip()
                    if text:
                        categories.append({
                            'name': text,
                            'element': elem,
                            'type': 'dropdown'
                        })
            except:
                pass
            
            # Try tree approach if dropdown failed
            if not categories:
                try:
                    tree_items = driver.find_elements(By.XPATH, "//ul[@class='jstree-children']//a")
                    for elem in tree_items:
                        text = elem.text.strip()
                        if text:
                            categories.append({
                                'name': text,
                                'element': elem,
                                'type': 'tree'
                            })
                except:
                    pass
            
            self.logger.info(f"Found {len(categories)} categories")
            return categories
            
        except Exception as e:
            self.logger.error(f"Failed to get categories: {e}")
            return []
    
    def select_category(self, driver, category: Dict) -> bool:
        """Select a specific category"""
        try:
            element = category['element']
            driver.execute_script("arguments[0].scrollIntoView(true);", element)
            time.sleep(1)
            driver.execute_script("arguments[0].click();", element)
            
            time.sleep(self.settings.scraping.delay_between_actions)
            self.logger.info(f"Selected category: {category['name']}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select category {category['name']}: {e}")
            return False
