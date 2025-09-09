#!/usr/bin/env python3
"""
Create final clean scraper with real product extraction
"""

def create_final_scraper():
    """Create the final clean scraper file"""
    
    content = '''"""
Wilo website scraper - Final version with real product extraction
"""

import time
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper.browser_manager import BrowserManager
from config.countries import get_country_config, COUNTRIES
from utils.logger import get_logger

class WiloScraper:
    """Main scraper for Wilo products with real extraction"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        
        # Callback for progress updates
        self.progress_callback = None
        self.products_callback = None
        
        # Categories
        self.categories = [
            "01. Heizung",
            "02. Trinkwarmwasser", 
            "03. Kältetechnik",
            "04. Klimatechnik",
            "05. Regenwasser",
            "06. Wasserversorgung und Druckerhöhung",
            "07. Wasseraufbereitung",
            "08. Rohwasserentnahme",
            "09. Abwassersammlung und -transport",
            "10. Entwässerung (einschl. Hochwasserschutz)",
            "11. Löschwasserversorgung",
            "12. Kommerzielle Bewässerung und Landwirtschaft",
            "13. Abwasserbehandlung"
        ]
        
        # Country mapping
        self.country_mapping = {
            'germany': 'Germany',
            'deutschland': 'Germany',
            'austria': 'Austria',
            'france': 'France',
            'italy': 'Italy',
            'spain': 'Spain',
            'netherlands': 'Netherlands',
            'poland': 'Poland',
            'united_kingdom': 'United Kingdom'
        }
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set callback for product updates"""
        self.products_callback = callback
        
    def start_scraping(self, country_key):
        """Start scraping process with real extraction"""
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
            time.sleep(5)
            
            self.browser_manager.take_screenshot("step1_initial_page.png")
            
            if self.progress_callback:
                self.progress_callback("Selecting country...")
            
            # Select country
            if not self._select_country(country_key):
                raise Exception("Failed to select country")
                
            if self.progress_callback:
                self.progress_callback("Navigating to pump selection...")
                
            # Navigate to hydraulic pump selection
            if not self._navigate_to_pump_selection():
                raise Exception("Failed to navigate to pump selection")
                
            if self.progress_callback:
                self.progress_callback("Starting REAL product extraction...")
                
            # Real product extraction - test with first category
            all_products = []
            test_category = self.categories[0]  # "01. Heizung"
            
            if self.progress_callback:
                self.progress_callback(f"Extracting REAL products from: {test_category}")
                
            category_products = self._extract_real_products_from_category(test_category)
            all_products.extend(category_products)
            
            # Update products in real-time
            if self.products_callback:
                for product in category_products:
                    self.products_callback(product)
                
            if self.progress_callback:
                self.progress_callback(f"REAL extraction completed! Found {len(all_products)} products", stop_progress=True)
                
            self.logger.info(f"REAL scraping completed. Found {len(all_products)} products")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Scraping failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Scraping failed: {e}", stop_progress=True)
            return []
        finally:
            self.browser_manager.quit()
    
    def _select_country(self, country_key):
        """Select country"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 20)
            
            english_country_name = self.country_mapping.get(country_key.lower(), 'Germany')
            self.logger.info(f"Looking for country span: {english_country_name}")
            
            self.browser_manager.take_screenshot("step2_before_country.png")
            
            try:
                country_span = wait.until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@class='btn-button-text'][text()='{english_country_name}']"))
                )
                
                driver.execute_script("arguments[0].scrollIntoView();", country_span)
                time.sleep(1)
                driver.execute_script("arguments[0].click();", country_span)
                self.logger.info(f"Successfully clicked country span: {english_country_name}")
                
                time.sleep(self.settings.page_load_delay)
                self.browser_manager.take_screenshot("step3_after_country.png")
                return True
                
            except Exception as e:
                self.logger.error(f"Could not find country span: {e}")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to select country: {e}")
            return False
    
    def _navigate_to_pump_selection(self):
        """Navigate to hydraulic pump selection with better waiting"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info("Looking for Hydraulische Pumpenauswahl tile...")
            self.logger.info("Waiting for page to fully load after country selection...")
            
            # Progressive waiting
            for wait_iteration in range(6):
                wait_time = (wait_iteration + 1) * 5
                
                self.logger.info(f"Waiting {wait_time} seconds for tiles to appear...")
                time.sleep(5)
                
                self.browser_manager.take_screenshot(f"step4_wait_{wait_time}s.png")
                
                # Look for pump-related tiles
                pump_keywords = ["Hydraulische", "Pumpen", "pump", "selection", "auswahl", "Pumpenauswahl"]
                tile_element = None
                
                for keyword in pump_keywords:
                    try:
                        elements = driver.find_elements(By.XPATH, f"//*[contains(translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz'), '{keyword.lower()}')]")
                        
                        for element in elements:
                            if element.is_displayed():
                                clickable_ancestor = element
                                for _ in range(5):
                                    try:
                                        if clickable_ancestor.tag_name in ['a', 'button', 'div', 'td'] and clickable_ancestor.is_enabled():
                                            element_text = element.text.strip()
                                            if len(element_text) > 10 and 'hydraul' in element_text.lower():
                                                tile_element = clickable_ancestor
                                                self.logger.info(f"Found tile with keyword '{keyword}': {element_text[:50]}")
                                                break
                                        clickable_ancestor = clickable_ancestor.find_element(By.XPATH, "./..")
                                    except:
                                        break
                                if tile_element:
                                    break
                        if tile_element:
                            break
                    except Exception as e:
                        continue
                
                if tile_element:
                    try:
                        driver.execute_script("arguments[0].scrollIntoView();", tile_element)
                        time.sleep(2)
                        driver.execute_script("arguments[0].click();", tile_element)
                        self.logger.info("Successfully clicked pump selection tile")
                        
                        time.sleep(self.settings.page_load_delay)
                        self.browser_manager.take_screenshot("step5_after_tile_click.png")
                        
                        time.sleep(3)
                        current_url = driver.current_url
                        self.logger.info(f"After tile click, current URL: {current_url}")
                        
                        return True
                        
                    except Exception as e:
                        self.logger.error(f"Failed to click tile element: {e}")
                        continue
                
                if wait_time >= 30:
                    break
            
            self.logger.error("Could not find pump selection tile after extended waiting")
            return False
                
        except Exception as e:
            self.logger.error(f"Failed to navigate to pump selection: {e}")
            return False
    
    def _extract_real_products_from_category(self, category):
        """Extract REAL products from category"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info(f"Extracting REAL products from category: {category}")
            
            # Take screenshot of current page state
            self.browser_manager.take_screenshot("step6_extraction_start.png")
            
            # Wait for page to load completely
            time.sleep(5)
            
            # Uncheck "Bilder ausblenden" to show images
            self._uncheck_image_hide_checkbox()
            
            # Extract products from current view
            all_products = []
            
            # Get subcategories and process them
            subcategories = self._get_subcategories_from_tree()
            self.logger.info(f"Found subcategories: {subcategories}")
            
            if subcategories:
                # Process each subcategory
                for i, subcategory in enumerate(subcategories[:3]):
                    if not self.is_running:
                        break
                        
                    self.logger.info(f"Processing subcategory {i+1}/{len(subcategories[:3])}: {subcategory}")
                    
                    # Click on subcategory
                    if self._click_subcategory(subcategory):
                        time.sleep(3)
                        
                        # Extract products from this subcategory
                        products = self._extract_products_from_current_view(category, subcategory)
                        all_products.extend(products)
                        
                        self.logger.info(f"Extracted {len(products)} products from {subcategory}")
            else:
                # If no subcategories, try to extract products directly
                self.logger.info("No subcategories found, extracting products directly")
                products = self._extract_products_from_current_view(category, "Direct")
                all_products.extend(products)
            
            self.logger.info(f"Total extracted {len(all_products)} REAL products from {category}")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract real products from category {category}: {e}")
            return []
    
    def _uncheck_image_hide_checkbox(self):
        """Uncheck 'Bilder ausblenden' to show product images"""
        try:
            driver = self.browser_manager.get_driver()
            
            checkbox_selectors = [
                "//input[@id='cbHideImg']",
                "//input[@name='cbHideImg']",
                "//input[contains(@onclick, 'onSeriesGridToggleMinimizedViewClicked')]",
                "//label[contains(text(), 'Bilder ausblenden')]//preceding-sibling::input",
                "//label[contains(text(), 'Bilder ausblenden')]//input",
                "//span[contains(text(), 'Bilder ausblenden')]//input"
            ]
            
            for selector in checkbox_selectors:
                try:
                    checkbox = driver.find_element(By.XPATH, selector)
                    if checkbox.is_displayed():
                        is_checked = checkbox.is_selected() or checkbox.get_attribute('checked')
                        
                        if is_checked:
                            driver.execute_script("arguments[0].click();", checkbox)
                            self.logger.info("Unchecked 'Bilder ausblenden' - Images should now be visible")
                            time.sleep(2)
                            self.browser_manager.take_screenshot("step7_images_enabled.png")
                        else:
                            self.logger.info("'Bilder ausblenden' already unchecked")
                        
                        return True
                except:
                    continue
            
            self.logger.warning("Could not find 'Bilder ausblenden' checkbox")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to uncheck image checkbox: {e}")
            return True
    
    def _get_subcategories_from_tree(self):
        """Get subcategories from the tree structure"""
        try:
            driver = self.browser_manager.get_driver()
            
            subcategory_selectors = [
                "//*[contains(text(), 'Umwälzpumpen')]",
                "//*[contains(text(), 'Inline-Pumpen')]",
                "//*[contains(text(), 'Blockpumpen')]",
                "//*[contains(text(), 'pumpen')]//parent::*",
                "//span[contains(text(), 'pumpen')]"
            ]
            
            subcategories = []
            for selector in subcategory_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed():
                            text = element.text.strip()
                            if text and len(text) > 5 and 'pump' in text.lower():
                                if text not in subcategories:
                                    subcategories.append(text)
                    
                    if subcategories:
                        break
                except:
                    continue
            
            clean_subcategories = []
            for subcat in subcategories[:5]:
                if len(subcat) > 8 and not any(x in subcat.lower() for x in ['©', '®', 'wilo']):
                    clean_subcategories.append(subcat)
            
            return clean_subcategories or ["Heizungspumpen"]
            
        except Exception as e:
            self.logger.error(f"Failed to get subcategories: {e}")
            return ["Heizungspumpen"]
    
    def _click_subcategory(self, subcategory):
        """Click on a specific subcategory"""
        try:
            driver = self.browser_manager.get_driver()
            
            subcategory_selectors = [
                f"//*[contains(text(), '{subcategory}')]",
                f"//a[contains(text(), '{subcategory[:15]}')]",
                f"//span[contains(text(), '{subcategory[:15]}')]",
                f"//div[contains(text(), '{subcategory[:15]}')]"
            ]
            
            for selector in subcategory_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for element in elements:
                        if element.is_displayed() and element.is_enabled():
                            driver.execute_script("arguments[0].click();", element)
                            self.logger.info(f"Clicked subcategory: {subcategory}")
                            time.sleep(3)
                            return True
                except:
                    continue
            
            self.logger.warning(f"Could not click subcategory: {subcategory}, continuing anyway")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to click subcategory: {e}")
            return True
    
    def _extract_products_from_current_view(self, category, subcategory):
        """Extract products from the current page view"""
        try:
            driver = self.browser_manager.get_driver()
            products = []
            
            self.browser_manager.take_screenshot(f"step8_products_{subcategory[:10]}.png")
            
            # Extract from grid rows (your HTML structure)
            grid_row_selectors = [
                "//tr[contains(@class, 'jqgrow')]",
                "//tr[contains(@class, 'ui-widget-content')]",
                "//tbody//tr[@role='row']"
            ]
            
            for selector in grid_row_selectors:
                try:
                    rows = driver.find_elements(By.XPATH, selector)
                    self.logger.info(f"Found {len(rows)} grid rows with selector: {selector}")
                    
                    for row in rows:
                        try:
                            # Extract product name from span with class 'common_lbl_bold'
                            name_element = row.find_element(By.XPATH, ".//span[@class='common_lbl_bold']")
                            product_name = name_element.text.strip()
                            
                            if not product_name or len(product_name) < 3:
                                continue
                            
                            # Extract image URL from background-image style
                            image_url = ""
                            try:
                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                                style_attr = img_div.get_attribute('style')
                                if 'url(' in style_attr:
                                    start = style_attr.find('url("') + 5
                                    end = style_attr.find('")', start)
                                    if start > 4 and end > start:
                                        relative_url = style_attr[start:end]
                                        # Convert to absolute URL
                                        if relative_url.startswith('ApplRangeHandler'):
                                            image_url = f"https://select.wilo.com/{relative_url}"
                                        else:
                                            image_url = relative_url
                            except:
                                pass
                            
                            # Create product object
                            product = {
                                'name': product_name,
                                'category': category,
                                'subcategory': subcategory,
                                'image_url': image_url,
                                'description': f"Wilo {product_name} - {subcategory}",
                                'specifications': {
                                    'brand': 'Wilo',
                                    'series': product_name,
                                    'application': subcategory
                                },
                                'price': 'Price on request',
                                'country': 'Germany',
                                'status': 'REAL Product - Extracted'
                            }
                            
                            products.append(product)
                            self.logger.info(f"Extracted REAL product: {product_name}")
                            
                        except Exception as row_error:
                            continue
                    
                    if products:
                        break
                        
                except Exception as selector_error:
                    continue
            
            # Fallback - look for any bold product names
            if not products:
                try:
                    name_elements = driver.find_elements(By.XPATH, "//span[@class='common_lbl_bold']")
                    for name_element in name_elements:
                        name = name_element.text.strip()
                        if name and len(name) > 3:
                            product = {
                                'name': name,
                                'category': category,
                                'subcategory': subcategory,
                                'image_url': '',
                                'description': f"Wilo {name}",
                                'specifications': {'brand': 'Wilo'},
                                'price': 'Price on request',
                                'country': 'Germany',
                                'status': 'REAL Product - Name Only'
                            }
                            products.append(product)
                            self.logger.info(f"Extracted REAL product (name only): {name}")
                except:
                    pass
            
            return products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from current view: {e}")
            return []
    
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
            
            time.sleep(5)
            self.browser_manager.take_screenshot("navigation_test.png")
            
            if "wilo" in driver.title.lower() or "select.wilo.com" in driver.current_url:
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
        f.write(content)
    
    print("Created final clean scraper with real product extraction")

def main():
    print("Creating Final Clean Scraper")
    print("=" * 30)
    
    create_final_scraper()
    
    print("\nFinal scraper created!")
    print("- Clean indentation throughout")
    print("- Real product extraction implemented")
    print("- Extracts product names and images")
    print("- Handles subcategories")
    print("- Unchecks image checkbox")
    print("\nTry running:")
    print("python main.py")

if __name__ == "__main__":
    main()