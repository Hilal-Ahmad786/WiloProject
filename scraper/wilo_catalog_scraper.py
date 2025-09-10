"""
Enhanced Wilo Catalog Scraper for new catalog page
Scrapes from: https://wilo.com/de/de/Katalog/de/anwendung/industrie/heizung/heizung
"""

import time
import re
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from scraper.browser_manager import BrowserManager
from utils.logger import get_logger

class WiloCatalogScraper:
    """New catalog scraper for Wilo products from catalog page"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        
        # Callback for progress updates
        self.progress_callback = None
        self.products_callback = None
        
        # Base URL for the new catalog
        self.catalog_url = "https://wilo.com/de/de/Katalog/de/anwendung/industrie/heizung/heizung"
        
    def set_progress_callback(self, callback):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def set_products_callback(self, callback):
        """Set callback for product updates"""
        self.products_callback = callback
        
    def start_scraping(self, max_products=2):
        """Start catalog scraping process"""
        try:
            self.is_running = True
            self.logger.info(f"Starting catalog scraping for max {max_products} products")
            
            if self.progress_callback:
                self.progress_callback("Initializing browser for catalog scraping...", start_progress=True)
            
            # Setup browser
            if not self.browser_manager.setup_driver():
                raise Exception("Failed to setup browser")
                
            driver = self.browser_manager.get_driver()
            
            if self.progress_callback:
                self.progress_callback("Navigating to Wilo catalog page...")
            
            # Navigate to catalog page
            self.logger.info("Navigating to Wilo catalog page...")
            driver.get(self.catalog_url)
            time.sleep(5)
            
            self.browser_manager.take_screenshot("catalog_step1_initial_page.png")
            
            if self.progress_callback:
                self.progress_callback("Finding product cards...")
                
            # Find and process product cards
            all_products = self._extract_products_from_cards(max_products)
            
            if self.progress_callback:
                self.progress_callback(f"Catalog scraping completed! Found {len(all_products)} products", stop_progress=True)
                
            self.logger.info(f"Catalog scraping completed. Found {len(all_products)} products")
            return all_products
            
        except Exception as e:
            self.logger.error(f"Catalog scraping failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Catalog scraping failed: {e}", stop_progress=True)
            return []
        finally:
            self.browser_manager.quit()
    
    def _extract_products_from_cards(self, max_products):
        """Extract products from card elements"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            # Wait for cards to load
            time.sleep(5)
            
            # Find all product cards using the structure you provided
            card_selector = "//div[contains(@class, 'card cl-overview h-100 rebrush')]"
            
            try:
                cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, card_selector)))
                self.logger.info(f"Found {len(cards)} product cards")
            except TimeoutException:
                self.logger.error("No product cards found")
                return []
            
            # Limit cards to max_products
            cards_to_process = cards[:max_products]
            self.logger.info(f"Processing {len(cards_to_process)} cards (limited by max_products={max_products})")
            
            all_products = []
            
            for i, card in enumerate(cards_to_process):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing product card {i+1}/{len(cards_to_process)}")
                
                try:
                    # Extract basic info from card
                    card_data = self._extract_card_data(card, i)
                    
                    if card_data:
                        # Click on card to go to product detail page
                        product_detail = self._get_product_details(card, card_data, i)
                        
                        if product_detail:
                            all_products.append(product_detail)
                            
                            # Update products in real-time
                            if self.products_callback:
                                self.products_callback(product_detail)
                            
                            self.logger.info(f"Successfully extracted product: {product_detail['name']}")
                        else:
                            self.logger.warning(f"Failed to get details for card {i+1}")
                    
                    # Small delay between cards
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"Error processing card {i+1}: {e}")
                    continue
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def _extract_card_data(self, card, index):
        """Extract data from a single product card"""
        try:
            # Extract product name from card footer
            try:
                name_element = card.find_element(By.XPATH, ".//div[@class='card-footer']//h3")
                product_name = name_element.text.strip()
            except:
                self.logger.warning(f"Could not find product name in card {index+1}")
                return None
            
            # Extract image from card
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    # Convert relative URL to absolute
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.warning(f"Could not find image in card {index+1}")
            
            # Extract product link
            product_link = ""
            try:
                link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                href = link_element.get_attribute('href')
                if href:
                    if href.startswith('/'):
                        product_link = f"https://wilo.com{href}"
                    else:
                        product_link = href
            except:
                self.logger.warning(f"Could not find product link in card {index+1}")
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
            }
            
            self.logger.info(f"Extracted card data: {product_name}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data: {e}")
            return None
    
    def _get_product_details(self, card, card_data, index):
        """Click on card and extract detailed product information"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Store current window handle
            main_window = driver.current_window_handle
            
            # Click on the card link
            try:
                link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                
                # Use JavaScript click to avoid potential overlay issues
                driver.execute_script("arguments[0].click();", link_element)
                self.logger.info(f"Clicked on product card: {card_data['name']}")
                
                # Wait for page to load
                time.sleep(5)
                
            except Exception as e:
                self.logger.error(f"Failed to click on card: {e}")
                return None
            
            # Take screenshot of product page
            self.browser_manager.take_screenshot(f"catalog_step2_product_{index}_page.png")
            
            # Extract detailed product information
            product_details = self._extract_product_page_details(card_data)
            
            # Go back to main page for next product
            driver.back()
            time.sleep(3)
            
            return product_details
            
        except Exception as e:
            self.logger.error(f"Failed to get product details: {e}")
            return None
    
    def _extract_product_page_details(self, card_data):
        """Extract detailed information from product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Extract all product images and videos
            media_items = self._extract_media_items()
            
            # Extract product short description (left side content)
            short_description = self._extract_short_description()
            
            # Extract advantages/benefits (Ihre Vorteile)
            advantages = self._extract_advantages()
            
            # Extract long description
            long_description = self._extract_long_description()
            
            # Create comprehensive product object
            product = {
                'id': f"catalog_{card_data['card_index']+1}_{int(time.time())}",
                'name': card_data['name'],
                'category': 'Industrie Heizung',
                'subcategory': 'Heizungspumpen',
                'source': 'catalog',
                
                # Images and media
                'card_image_url': card_data['card_image_url'],
                'product_images': media_items['images'],
                'product_videos': media_items['videos'],
                'all_media': media_items['all_media'],
                
                # Descriptions
                'short_description': short_description,
                'advantages': advantages,
                'long_description': long_description,
                'full_description': self._build_full_description(short_description, advantages, long_description),
                
                # Additional data
                'product_url': driver.current_url,
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'specifications': {
                    'brand': 'Wilo',
                    'series': card_data['name'],
                    'application': 'Industrie Heizung',
                    'type': 'Heizungspumpe'
                },
                'price': 'Price on request',
                'currency': 'EUR',
                'country': 'Germany',
                'status': 'Catalog Product - Real Extraction'
            }
            
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to extract product page details: {e}")
            return None
    
    def _extract_media_items(self):
        """Extract all images and videos from product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            media_items = {
                'images': [],
                'videos': [],
                'all_media': []
            }
            
            # Find all images on the product page
            try:
                # Look for carousel or gallery images
                img_selectors = [
                    "//div[contains(@class, 'carousel')]//img",
                    "//div[contains(@class, 'gallery')]//img", 
                    "//div[contains(@class, 'cl-gutters')]//img",
                    "//img[contains(@src, 'wilo')]"
                ]
                
                for selector in img_selectors:
                    try:
                        images = driver.find_elements(By.XPATH, selector)
                        for img in images:
                            src = img.get_attribute('src')
                            if src and src not in media_items['images']:
                                # Convert to absolute URL
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                media_items['images'].append(src)
                                media_items['all_media'].append({
                                    'type': 'image',
                                    'url': src,
                                    'alt': img.get_attribute('alt') or ''
                                })
                    except:
                        continue
                
            except Exception as e:
                self.logger.debug(f"Image extraction failed: {e}")
            
            # Find videos
            try:
                video_selectors = [
                    "//video//source",
                    "//iframe[contains(@src, 'video')]",
                    "//div[contains(@class, 'video')]//iframe"
                ]
                
                for selector in video_selectors:
                    try:
                        videos = driver.find_elements(By.XPATH, selector)
                        for video in videos:
                            src = video.get_attribute('src')
                            if src and src not in media_items['videos']:
                                media_items['videos'].append(src)
                                media_items['all_media'].append({
                                    'type': 'video',
                                    'url': src,
                                    'title': ''
                                })
                    except:
                        continue
                        
            except Exception as e:
                self.logger.debug(f"Video extraction failed: {e}")
            
            self.logger.info(f"Extracted {len(media_items['images'])} images and {len(media_items['videos'])} videos")
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract media items: {e}")
            return {'images': [], 'videos': [], 'all_media': []}
    
    def _extract_short_description(self):
        """Extract short description from left side of product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            short_desc_selectors = [
                "//div[contains(@class, 'product-info')]//p",
                "//div[contains(@class, 'description')]//p",
                "//h3[following-sibling::div/p]//following-sibling::div//p",
                "//div[@class='pl-md-8']//p"
            ]
            
            short_description = ""
            
            for selector in short_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    if elements:
                        paragraphs = []
                        for elem in elements:
                            text = elem.text.strip()
                            if text and len(text) > 20:  # Only meaningful paragraphs
                                paragraphs.append(text)
                        
                        if paragraphs:
                            short_description = " ".join(paragraphs)
                            break
                            
                except:
                    continue
            
            self.logger.info(f"Extracted short description: {len(short_description)} characters")
            return short_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract short description: {e}")
            return ""
    
    def _extract_advantages(self):
        """Extract advantages/benefits (Ihre Vorteile) section"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for the advantages section with "Ihre Vorteile" header
            advantages_selectors = [
                "//div[contains(@class, 'cl-your-advantages')]//ul//li",
                "//h3[contains(text(), 'Ihre Vorteile')]//following-sibling::div//ul//li",
                "//h3[contains(text(), 'Vorteile')]//following-sibling::div//ul//li"
            ]
            
            advantages = []
            
            for selector in advantages_selectors:
                try:
                    li_elements = driver.find_elements(By.XPATH, selector)
                    if li_elements:
                        for li in li_elements:
                            text = li.text.strip()
                            if text:
                                advantages.append(text)
                        break
                except:
                    continue
            
            self.logger.info(f"Extracted {len(advantages)} advantages")
            return advantages
            
        except Exception as e:
            self.logger.error(f"Failed to extract advantages: {e}")
            return []
    
    def _extract_long_description(self):
        """Extract long description and other content sections"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for various content sections
            long_desc_selectors = [
                "//div[contains(@class, 'description')]",
                "//div[contains(@class, 'content')]//div[contains(@class, 'text')]",
                "//div[contains(@class, 'product-details')]",
                "//div[contains(@class, 'two-cols-section')]//div[contains(@class, 'text-module')]"
            ]
            
            long_description_parts = []
            
            for selector in long_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:  # Only substantial content
                            # Clean up the text
                            text = re.sub(r'\s+', ' ', text)  # Normalize whitespace
                            if text not in long_description_parts:
                                long_description_parts.append(text)
                except:
                    continue
            
            long_description = "\n\n".join(long_description_parts)
            
            self.logger.info(f"Extracted long description: {len(long_description)} characters")
            return long_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract long description: {e}")
            return ""
    
    def _build_full_description(self, short_desc, advantages, long_desc):
        """Build comprehensive description for Shopify"""
        try:
            html_parts = []
            
            # Short description
            if short_desc:
                html_parts.append(f"<div class='product-intro'>{short_desc}</div>")
            
            # Advantages
            if advantages:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    html_parts.append(f"<li>{advantage}</li>")
                html_parts.append("</ul>")
            
            # Long description
            if long_desc:
                # Split long description into paragraphs
                paragraphs = long_desc.split('\n\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            # Brand information
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender Hersteller von Pumpen und Pumpensystemen für Heizung, Kühlung, Klimatechnik, Wasserversorgung und Abwasserbehandlung.</p>")
            
            return "\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to build full description: {e}")
            return short_desc or "Wilo Produkt"
    
    def test_navigation(self):
        """Test navigation to catalog page"""
        try:
            self.logger.info("Testing catalog navigation...")
            
            if self.progress_callback:
                self.progress_callback("Testing catalog navigation...", start_progress=True)
            
            if not self.browser_manager.setup_driver():
                return False
                
            driver = self.browser_manager.get_driver()
            driver.get(self.catalog_url)
            
            time.sleep(5)
            self.browser_manager.take_screenshot("catalog_navigation_test.png")
            
            # Check if we're on the right page
            if "wilo.com" in driver.current_url and "katalog" in driver.current_url.lower():
                self.logger.info("Catalog navigation test completed successfully")
                if self.progress_callback:
                    self.progress_callback("Catalog navigation test successful!", stop_progress=True)
                return True
            else:
                self.logger.error("Catalog navigation test failed - unexpected page")
                if self.progress_callback:
                    self.progress_callback("Catalog navigation test failed", stop_progress=True)
                return False
            
        except Exception as e:
            self.logger.error(f"Catalog navigation test failed: {e}")
            if self.progress_callback:
                self.progress_callback(f"Catalog navigation test failed: {e}", stop_progress=True)
            return False
        finally:
            self.browser_manager.quit()
    
    def stop(self):
        """Stop scraping"""
        self.logger.info("Stopping catalog scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Catalog scraping stopped by user", stop_progress=True)
