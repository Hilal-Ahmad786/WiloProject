"""
Product data extraction logic
"""

from selenium.webdriver.common.by import By
from utils.logger import get_logger
from datetime import datetime
from typing import Dict, Optional

class ProductExtractor:
    """Extracts product data from product pages"""
    
    def __init__(self, settings):
        self.settings = settings
        self.logger = get_logger(__name__)
    
    def extract_product_data(self, driver, category: str, country: str) -> Optional[Dict]:
        """Extract product data from current page"""
        try:
            data = {
                'category': category,
                'country': country,
                'scraped_at': datetime.now().isoformat()
            }
            
            # Extract product name
            try:
                name_selectors = [
                    "//h1", "//h2", "//*[@class='product-title']",
                    "//*[contains(@class, 'title')]", "//*[contains(@class, 'name')]"
                ]
                
                for selector in name_selectors:
                    try:
                        name_element = driver.find_element(By.XPATH, selector)
                        if name_element.text.strip():
                            data['name'] = name_element.text.strip()
                            break
                    except:
                        continue
                
                if 'name' not in data:
                    data['name'] = "Unknown Product"
                    
            except Exception as e:
                data['name'] = "Unknown Product"
                self.logger.warning(f"Failed to extract product name: {e}")
            
            # Extract specifications
            specs = {}
            try:
                spec_elements = driver.find_elements(By.XPATH, "//table//tr")
                for row in spec_elements:
                    try:
                        cells = row.find_elements(By.XPATH, ".//td")
                        if len(cells) >= 2:
                            key = cells[0].text.strip()
                            value = cells[1].text.strip()
                            if key and value:
                                specs[key] = value
                    except:
                        continue
            except:
                pass
            
            data['specifications'] = specs
            
            # Extract price
            try:
                price_selectors = [
                    "//*[contains(@class, 'price')]",
                    "//*[contains(text(), '€')]",
                    "//*[contains(text(), '$')]"
                ]
                
                for selector in price_selectors:
                    try:
                        price_element = driver.find_element(By.XPATH, selector)
                        if price_element.text.strip():
                            data['price'] = price_element.text.strip()
                            break
                    except:
                        continue
                
                if 'price' not in data:
                    data['price'] = "Price not available"
                    
            except:
                data['price'] = "Price not available"
            
            # Extract description
            try:
                desc_selectors = [
                    "//div[@class='description']",
                    "//*[contains(@class, 'desc')]",
                    "//p[contains(@class, 'description')]"
                ]
                
                for selector in desc_selectors:
                    try:
                        desc_element = driver.find_element(By.XPATH, selector)
                        if desc_element.text.strip():
                            data['description'] = desc_element.text.strip()
                            break
                    except:
                        continue
                
                if 'description' not in data:
                    data['description'] = ""
                    
            except:
                data['description'] = ""
            
            # Extract images
            if self.settings.scraping.download_images:
                try:
                    img_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'product')]")
                    data['images'] = [
                        img.get_attribute('src') 
                        for img in img_elements 
                        if img.get_attribute('src')
                    ]
                except:
                    data['images'] = []
            else:
                data['images'] = []
            
            return data
            
        except Exception as e:
            self.logger.error(f"Failed to extract product data: {e}")
            return None
