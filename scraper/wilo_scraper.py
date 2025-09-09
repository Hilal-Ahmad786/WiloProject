"""
Enhanced Wilo website scraper - Multiple categories with better extraction
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
    """Enhanced scraper for Wilo products with multi-category support"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        
        # Callback for progress updates
        self.progress_callback = None
        self.products_callback = None
        
        # All 13 categories from the website
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
        
        # Country mapping for website
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
        """Start enhanced scraping process with multiple categories"""
        try:
            self.is_running = True
            self.logger.info(f"Starting enhanced scraping for country: {country_key}")
            
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
                self.progress_callback("Starting multi-category extraction...")
                
            # Enhanced multi-category extraction
            all_products = []
            
            # Process multiple categories (limit for testing)
            categories_to_process = self.categories[:1]  # First 3 categories for testing
            
            for i, category in enumerate(categories_to_process):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing category {i+1}/{len(categories_to_process)}: {category}")
                    
                # Extract products from this category
                category_products = self._extract_products_from_category(category, i)
                all_products.extend(category_products)
                
                # Update products in real-time
                if self.products_callback:
                    for product in category_products:
                        self.products_callback(product)
                
                self.logger.info(f"Extracted {len(category_products)} products from {category}")
                
                # Small delay between categories
                time.sleep(2)
                
            if self.progress_callback:
                self.progress_callback(f"Enhanced extraction completed! Found {len(all_products)} products", stop_progress=True)
                
            self.logger.info(f"Enhanced scraping completed. Found {len(all_products)} products total")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Enhanced scraping failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Scraping failed: {e}", stop_progress=True)
            return []
        finally:
            self.browser_manager.quit()
    
    def _select_country(self, country_key):
        """Select country (same as before)"""
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
        """Navigate to pump selection (enhanced with better waiting)"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info("Looking for Hydraulische Pumpenauswahl tile...")
            self.logger.info("Waiting for page to fully load after country selection...")
            
            # Progressive waiting with better detection
            for wait_iteration in range(6):
                wait_time = (wait_iteration + 1) * 5
                
                self.logger.info(f"Waiting {wait_time} seconds for tiles to appear...")
                time.sleep(5)
                
                self.browser_manager.take_screenshot(f"step4_wait_{wait_time}s.png")
                
                # Enhanced tile detection
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
    
    def _extract_products_from_category(self, category, category_index):
        """Enhanced product extraction from each category"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info(f"Extracting products from category: {category}")
            
            # Take screenshot at start of category
            self.browser_manager.take_screenshot(f"step6_category_{category_index}_start.png")
            
            # Step 1: Select category from dropdown if needed
            if not self._select_category_from_dropdown(category):
                self.logger.warning(f"Could not select category {category}, using current selection")
            
            # Step 2: Uncheck "Bilder ausblenden" to show images
            self._uncheck_image_hide_checkbox()
            
            # Step 3: Get and process subcategories
            subcategories = self._get_subcategories_for_category(category)
            self.logger.info(f"Found {len(subcategories)} subcategories for {category}")
            
            all_products = []
            
            # Process each subcategory
            for j, subcategory in enumerate(subcategories[:2]):  # Limit to 2 subcategories per category
                if not self.is_running:
                    break
                    
                self.logger.info(f"Processing subcategory {j+1}/{len(subcategories[:2])}: {subcategory}")
                
                # Click on subcategory
                if self._click_subcategory(subcategory):
                    time.sleep(3)
                    
                    # Extract products from this subcategory
                    products = self._extract_products_from_current_view(category, subcategory)
                    all_products.extend(products)
                    
                    self.logger.info(f"Extracted {len(products)} products from {subcategory}")
                    
                    # Take screenshot after subcategory
                    self.browser_manager.take_screenshot(f"step7_cat{category_index}_sub{j}_products.png")
            
            # If no subcategories, extract directly
            if not subcategories:
                self.logger.info("No subcategories found, extracting products directly")
                products = self._extract_products_from_current_view(category, "Direct")
                all_products.extend(products)
            
            self.logger.info(f"Total extracted {len(all_products)} products from {category}")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from category {category}: {e}")
            return []
    
    def _select_category_from_dropdown(self, category):
        """Select category from Einsatzgebiet dropdown"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for category dropdown
            dropdown_selectors = [
                "//select[contains(@id, 'ddARKey')]",
                "//div[contains(@class, 'RadComboBox')]//input",
                "//input[contains(@id, 'ddARKey')]"
            ]
            
            for selector in dropdown_selectors:
                try:
                    dropdown = driver.find_element(By.XPATH, selector)
                    if dropdown.is_displayed():
                        # Check current selection
                        current_text = dropdown.get_attribute('value') or dropdown.text
                        if category in current_text:
                            self.logger.info(f"Category {category} already selected")
                            return True
                        
                        # Try to select the category
                        dropdown.click()
                        time.sleep(1)
                        
                        # Look for category option
                        category_option = driver.find_element(By.XPATH, f"//li[contains(text(), '{category}')]")
                        category_option.click()
                        self.logger.info(f"Selected category: {category}")
                        time.sleep(2)
                        return True
                except:
                    continue
            
            self.logger.info(f"Category dropdown not found or {category} already selected")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to select category: {e}")
            return True
    
    def _uncheck_image_hide_checkbox(self):
        """Uncheck 'Bilder ausblenden' to show product images - ENHANCED"""
        try:
            driver = self.browser_manager.get_driver()
            
            self.logger.info("🖼️ Looking for 'Bilder ausblenden' checkbox to show images...")
            
            # Multiple strategies to find the checkbox
            checkbox_selectors = [
                "//input[@id='cbHideImg']",
                "//input[@name='cbHideImg']", 
                "//input[contains(@onclick, 'onSeriesGridToggleMinimizedViewClicked')]",
                "//input[contains(@onclick, 'HideImg')]",
                "//label[contains(text(), 'Bilder ausblenden')]//input",
                "//label[contains(text(), 'Bilder ausblenden')]//preceding-sibling::input",
                "//span[contains(text(), 'Bilder ausblenden')]//input",
                "//span[contains(text(), 'Bilder ausblenden')]//preceding-sibling::input",
                "//div[contains(text(), 'Bilder ausblenden')]//input",
                "//input[@type='checkbox'][following-sibling::*[contains(text(), 'Bilder ausblenden')]]",
                "//input[@type='checkbox'][preceding-sibling::*[contains(text(), 'Bilder ausblenden')]]"
            ]
            
            checkbox_found = False
            
            for i, selector in enumerate(checkbox_selectors):
                try:
                    self.logger.debug(f"Trying selector {i+1}: {selector}")
                    checkboxes = driver.find_elements(By.XPATH, selector)
                    
                    for checkbox in checkboxes:
                        if checkbox.is_displayed():
                            # Check current state
                            is_checked = checkbox.is_selected() or checkbox.get_attribute('checked') == 'true'
                            
                            self.logger.info(f"Found 'Bilder ausblenden' checkbox (selector {i+1})")
                            self.logger.info(f"Current state: {'CHECKED' if is_checked else 'UNCHECKED'}")
                            
                            if is_checked:
                                # Uncheck it to show images
                                try:
                                    driver.execute_script("arguments[0].click();", checkbox)
                                    self.logger.info("✅ Successfully UNCHECKED 'Bilder ausblenden' with JavaScript click")
                                    checkbox_found = True
                                except:
                                    try:
                                        checkbox.click()
                                        self.logger.info("✅ Successfully UNCHECKED 'Bilder ausblenden' with regular click")
                                        checkbox_found = True
                                    except:
                                        self.logger.warning("Failed to click checkbox, trying to set attribute directly")
                                        try:
                                            driver.execute_script("arguments[0].checked = false;", checkbox)
                                            driver.execute_script("arguments[0].dispatchEvent(new Event('change'));", checkbox)
                                            self.logger.info("✅ Successfully UNCHECKED 'Bilder ausblenden' by setting attribute")
                                            checkbox_found = True
                                        except:
                                            continue
                                
                                # Wait for page to update
                                time.sleep(2)
                                
                                # Take screenshot to verify
                                self.browser_manager.take_screenshot("step7_images_enabled_verification.png")
                                
                                # Verify the change
                                try:
                                    new_state = checkbox.is_selected() or checkbox.get_attribute('checked') == 'true'
                                    if not new_state:
                                        self.logger.info("🖼️ Images should now be VISIBLE!")
                                    else:
                                        self.logger.warning("⚠️ Checkbox might still be checked")
                                except:
                                    pass
                                
                                break
                            else:
                                self.logger.info("✅ 'Bilder ausblenden' already UNCHECKED - Images should be visible")
                                checkbox_found = True
                                break
                    
                    if checkbox_found:
                        break
                        
                except Exception as e:
                    self.logger.debug(f"Selector {i+1} failed: {e}")
                    continue
            
            if not checkbox_found:
                self.logger.warning("⚠️ Could not find 'Bilder ausblenden' checkbox")
                
                # Debug: Look for any checkboxes on the page
                try:
                    all_checkboxes = driver.find_elements(By.XPATH, "//input[@type='checkbox']")
                    self.logger.info(f"Found {len(all_checkboxes)} total checkboxes on page")
                    
                    for i, cb in enumerate(all_checkboxes[:10]):  # Check first 10
                        try:
                            if cb.is_displayed():
                                # Get surrounding text
                                parent = cb.find_element(By.XPATH, ".//..")
                                surrounding_text = parent.text.strip()[:100]
                                self.logger.debug(f"Checkbox {i+1}: {surrounding_text}")
                                
                                # If it contains image-related text, try it
                                if any(word in surrounding_text.lower() for word in ['bild', 'image', 'hide', 'ausblend']):
                                    self.logger.info(f"Found potential image checkbox: {surrounding_text}")
                                    if cb.is_selected():
                                        try:
                                            driver.execute_script("arguments[0].click();", cb)
                                            self.logger.info("✅ Unchecked potential image hiding checkbox")
                                            time.sleep(1)
                                            checkbox_found = True
                                            break
                                        except:
                                            continue
                        except:
                            continue
                except Exception as e:
                    self.logger.debug(f"Debug checkbox search failed: {e}")
            
            # Final verification - look for visible images
            try:
                time.sleep(2)  # Wait for any dynamic loading
                
                # Check if there are any product images visible now
                image_elements = driver.find_elements(By.XPATH, "//img[contains(@src, 'ApplRangeHandler')] | //*[contains(@style, 'background-image') and contains(@style, 'ApplRangeHandler')]")
                
                if image_elements:
                    visible_images = [img for img in image_elements if img.is_displayed()]
                    self.logger.info(f"🖼️ Found {len(visible_images)} visible product images on page")
                else:
                    self.logger.warning("⚠️ No product images found - they might still be hidden")
                    
                    # Take a debug screenshot
                    self.browser_manager.take_screenshot("debug_no_images_found.png")
                    
            except Exception as e:
                self.logger.debug(f"Image verification failed: {e}")
            
            return checkbox_found
            
        except Exception as e:
            self.logger.error(f"Failed to uncheck image checkbox: {e}")
            return False

    def _get_subcategories_for_category(self, category):
        """Get subcategories specific to the current category"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Category-specific subcategory patterns
            category_subcategories = {
                "01. Heizung": ["Umwälzpumpen", "Inline-Pumpen", "Blockpumpen"],
                "02. Trinkwarmwasser": ["Trinkwasser-Pumpen", "Brauchwasser-Pumpen"],
                "03. Kältetechnik": ["Kälte-Umwälzpumpen", "Kühlwasser-Pumpen"],
                "04. Klimatechnik": ["Klima-Umwälzpumpen", "Lüftungsanlagen"],
                "05. Regenwasser": ["Regenwasser-Pumpen", "Zisternenpumpen"]
            }
            
            # First try to get category-specific subcategories
            if category in category_subcategories:
                return category_subcategories[category]
            
            # Otherwise, look for general subcategories on the page
            subcategory_selectors = [
                "//div[contains(@class, 'tree')]//a",
                "//ul//li//a",
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
            
            # Clean and limit subcategories
            clean_subcategories = []
            for subcat in subcategories[:3]:  # Limit to 3
                if len(subcat) > 8 and not any(x in subcat.lower() for x in ['©', '®', 'wilo']):
                    clean_subcategories.append(subcat)
            
            return clean_subcategories or ["Standard Pumpen"]
            
        except Exception as e:
            self.logger.error(f"Failed to get subcategories: {e}")
            return ["Standard Pumpen"]
    
    def _click_subcategory(self, subcategory):
        """Click on a specific subcategory"""
        try:
            driver = self.browser_manager.get_driver()
            
            subcategory_selectors = [
                f"//*[contains(text(), '{subcategory}')]",
                f"//a[contains(text(), '{subcategory[:15]}')]",
                f"//span[contains(text(), '{subcategory[:15]}')]"
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
        """Extract products from current page view with ENHANCED IMAGE extraction"""
        try:
            driver = self.browser_manager.get_driver()
            products = []
            
            self.browser_manager.take_screenshot(f"step8_products_{subcategory[:10]}.png")
            
            # Look for product grid rows
            grid_row_selectors = [
                "//tr[contains(@class, 'jqgrow')]",
                "//tr[contains(@class, 'ui-widget-content')]",
                "//tbody//tr[@role='row']"
            ]
            
            for selector in grid_row_selectors:
                try:
                    rows = driver.find_elements(By.XPATH, selector)
                    self.logger.info(f"Found {len(rows)} grid rows with selector: {selector}")
                    
                    for i, row in enumerate(rows):
                        try:
                            # Extract product name
                            name_element = row.find_element(By.XPATH, ".//span[@class='common_lbl_bold']")
                            product_name = name_element.text.strip()
                            
                            if not product_name or len(product_name) < 3:
                                continue
                            
                            # ENHANCED IMAGE EXTRACTION
                            image_url = ""
                            try:
                                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                                style_attr = img_div.get_attribute('style')
                                if 'url(' in style_attr:
                                    start = style_attr.find('url("') + 5
                                    end = style_attr.find('")', start)
                                    if start > 4 and end > start:
                                        relative_url = style_attr[start:end]
                                        # Decode HTML entities
                                        relative_url = relative_url.replace('&quot;', '"').replace('&amp;', '&')
                                        # Convert to absolute URL
                                        if relative_url.startswith('ApplRangeHandler'):
                                            image_url = f"https://select.wilo.com/{relative_url}"
                                        else:
                                            image_url = relative_url
                                        self.logger.info(f"✅ IMAGE FOUND for {product_name}: {image_url}")
                            except:
                                self.logger.warning(f"❌ NO IMAGE found for {product_name}")
                            
                            except Exception as row_error:
                            self.logger.error(f"Error processing row: {row_error}")
                            continue
                    
                    if products:
                        break
                        
                except Exception as selector_error:
                    self.logger.error(f"Error with selector {selector}: {selector_error}")
                    continue
            
            # Debug: Take screenshot showing current page state
            if products:
                self.browser_manager.take_screenshot(f"step9_extracted_products_{subcategory[:10]}.png")
                
                # Log summary
                with_images = sum(1 for p in products if p['has_image'])
                without_images = len(products) - with_images
                self.logger.info(f"📊 EXTRACTION SUMMARY for {subcategory}:")
                self.logger.info(f"   Total products: {len(products)}")
                self.logger.info(f"   With images: {with_images}")
                self.logger.info(f"   Without images: {without_images}")
            
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
            
    def _extract_sprite_image_info(self, row, product_index):
        """Extract sprite sheet image information from product row"""
        try:
            image_info = {
                'image_url': '',
                'sprite_sheet_url': '',
                'sprite_position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64}
            }
            
            # Look for div with background-image style
            try:
                img_div = row.find_element(By.XPATH, ".//div[contains(@style, 'background-image')]")
                style_attr = img_div.get_attribute('style')
                
                if 'url(' in style_attr:
                    # Extract URL from style
                    start = style_attr.find('url("') + 5
                    if start == 4:  # Try without quotes
                        start = style_attr.find('url(') + 4
                        end = style_attr.find(')', start)
                    else:
                        end = style_attr.find('")', start)
                    
                    if start > 4 and end > start:
                        relative_url = style_attr[start:end]
                        
                        # Decode HTML entities
                        relative_url = relative_url.replace('&quot;', '"').replace('&amp;', '&')
                        
                        # Build full URL
                        if relative_url.startswith('ApplRangeHandler'):
                            sprite_sheet_url = f"https://select.wilo.com/{relative_url}"
                        elif relative_url.startswith('http'):
                            sprite_sheet_url = relative_url
                        else:
                            sprite_sheet_url = f"https://select.wilo.com/{relative_url}"
                        
                        image_info['sprite_sheet_url'] = sprite_sheet_url
                        image_info['image_url'] = sprite_sheet_url  # Use sprite as image for now
                        
                        # Extract background-position
                        position_info = self._extract_background_position(style_attr)
                        image_info['sprite_position'] = position_info
                        
                        # Extract dimensions  
                        dimensions = self._extract_element_dimensions(img_div)
                        image_info['dimensions'] = dimensions
                        
                        self.logger.debug(f"Sprite URL: {sprite_sheet_url}")
                        self.logger.debug(f"Position: {position_info}")
                        
            except Exception as e:
                self.logger.debug(f"Background-image extraction failed: {e}")
            
            return image_info
            
        except Exception as e:
            self.logger.error(f"Failed to extract sprite image info: {e}")
            return {
                'image_url': '',
                'sprite_sheet_url': '',
                'sprite_position': {'x': 0, 'y': 0},
                'dimensions': {'width': 64, 'height': 64}
            }
    
    def _extract_background_position(self, style_attr):
        """Extract background-position from CSS style"""
        try:
            # Simple string search for background-position
            if 'background-position:' in style_attr:
                start_idx = style_attr.find('background-position:') + len('background-position:')
                end_idx = style_attr.find(';', start_idx)
                if end_idx == -1:
                    end_idx = len(style_attr)
                
                position_value = style_attr[start_idx:end_idx].strip()
                
                # Parse position (e.g., "0px 0px", "-64px -128px")
                parts = position_value.split()
                if len(parts) >= 2:
                    x_str = parts[0].replace('px', '').replace(',', '')
                    y_str = parts[1].replace('px', '').replace(',', '')
                    
                    try:
                        x = int(float(x_str))
                        y = int(float(y_str))
                        return {'x': abs(x), 'y': abs(y)}
                    except ValueError:
                        pass
            
            return {'x': 0, 'y': 0}
            
        except Exception as e:
            self.logger.debug(f"Background position extraction failed: {e}")
            return {'x': 0, 'y': 0}
    
    def _extract_element_dimensions(self, element):
        """Extract width and height from element"""
        try:
            style = element.get_attribute('style')
            width = height = 64  # Default
            
            # Simple string parsing for dimensions
            if 'width:' in style:
                start_idx = style.find('width:') + len('width:')
                end_idx = style.find('px', start_idx)
                if end_idx > start_idx:
                    try:
                        width = int(style[start_idx:end_idx].strip())
                    except ValueError:
                        pass
            
            if 'height:' in style:
                start_idx = style.find('height:') + len('height:')
                end_idx = style.find('px', start_idx)
                if end_idx > start_idx:
                    try:
                        height = int(style[start_idx:end_idx].strip())
                    except ValueError:
                        pass
            
            return {'width': width, 'height': height}
            
        except Exception as e:
            self.logger.debug(f"Dimension extraction failed: {e}")
            return {'width': 64, 'height': 64}


    def stop(self):
        """Stop scraping"""
        self.logger.info("Stopping enhanced scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Scraping stopped by user", stop_progress=True)
