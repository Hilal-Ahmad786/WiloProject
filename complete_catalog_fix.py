#!/usr/bin/env python3
"""
Complete fix for catalog scraper - rebuild the entire file to fix all indentation issues
"""

def rebuild_catalog_scraper():
    """Rebuild the entire catalog scraper with correct indentation"""
    
    complete_scraper_content = '''"""
Enhanced Wilo Catalog Scraper for new catalog page
Scrapes from: https://wilo.com/de/de/Katalog/de/anwendung/industrie/heizung/heizung
Updated to extract specific elements from product pages
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
        """Extract products from card elements with enhanced error handling"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            # Wait for cards to load
            time.sleep(5)
            
            # Find all product cards using multiple selectors
            card_selectors = [
                "//div[contains(@class, 'card cl-overview h-100 rebrush')]",
                "//div[contains(@class, 'card') and contains(@class, 'cl-overview')]",
                "//div[@class='card cl-overview h-100 rebrush']"
            ]
            
            cards = []
            for selector in card_selectors:
                try:
                    found_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                    if found_cards:
                        cards = found_cards
                        self.logger.info(f"Found {len(cards)} product cards with selector: {selector}")
                        break
                except TimeoutException:
                    continue
            
            if not cards:
                self.logger.error("No product cards found with any selector")
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
                    self.logger.info(f"\\n=== PROCESSING CARD {i+1} ===")
                    
                    # Extract basic info from card
                    card_data = self._extract_card_data(card, i)
                    
                    if card_data and card_data.get('name'):
                        self.logger.info(f"Card {i+1} extracted successfully: {card_data['name']}")
                        
                        # Only click and extract details if we have a valid link
                        if card_data.get('product_link'):
                            # Click on card to go to product detail page
                            product_detail = self._get_product_details(card, card_data, i)
                            
                            if product_detail:
                                all_products.append(product_detail)
                                
                                # Update products in real-time
                                if self.products_callback:
                                    self.products_callback(product_detail)
                                
                                self.logger.info(f"✅ Successfully extracted product: {product_detail['name']}")
                            else:
                                self.logger.warning(f"❌ Failed to get details for card {i+1}")
                        else:
                            self.logger.warning(f"⚠️  No product link found for card {i+1}, skipping detail extraction")
                    else:
                        self.logger.warning(f"❌ Failed to extract basic data from card {i+1}")
                    
                    # Small delay between cards
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing card {i+1}: {e}")
                    continue
            
            self.logger.info(f"\\n=== EXTRACTION COMPLETE ===")
            self.logger.info(f"Successfully processed {len(all_products)} out of {len(cards_to_process)} cards")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def _extract_card_data(self, card, index):
        """Extract data from a single product card with better error handling"""
        try:
            # Multiple strategies to extract product name
            product_name = ""
            
            # Strategy 1: Card footer h3
            try:
                name_element = card.find_element(By.XPATH, ".//div[@class='card-footer']//h3")
                product_name = name_element.text.strip()
                self.logger.debug(f"Found name via card-footer h3: {product_name}")
            except:
                pass
            
            # Strategy 2: Any h3 in the card
            if not product_name:
                try:
                    name_element = card.find_element(By.XPATH, ".//h3")
                    product_name = name_element.text.strip()
                    self.logger.debug(f"Found name via any h3: {product_name}")
                except:
                    pass
            
            # Strategy 3: Card title attribute or alt text
            if not product_name:
                try:
                    title_element = card.find_element(By.XPATH, ".//*[@title]")
                    product_name = title_element.get_attribute('title').strip()
                    self.logger.debug(f"Found name via title attribute: {product_name}")
                except:
                    pass
            
            # Strategy 4: Any text content that looks like a product name
            if not product_name:
                try:
                    text_elements = card.find_elements(By.XPATH, ".//*[text()]")
                    for elem in text_elements:
                        text = elem.text.strip()
                        # Look for text that contains "Wilo" and is substantial
                        if text and len(text) > 5 and ('wilo' in text.lower() or 'atmos' in text.lower() or 'pump' in text.lower()):
                            product_name = text
                            self.logger.debug(f"Found name via text content: {product_name}")
                            break
                except:
                    pass
            
            # Strategy 5: Use a fallback name based on index
            if not product_name:
                product_name = f"Wilo Product {index + 1}"
                self.logger.warning(f"Using fallback name for card {index + 1}: {product_name}")
            
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
            
            # Extract product link with multiple strategies
            product_link = ""
            link_selectors = [
                ".//a[@class='stretched-link']",
                ".//a[contains(@class, 'stretched')]",
                ".//a[@href]",
                ".//a"
            ]
            
            for selector in link_selectors:
                try:
                    link_element = card.find_element(By.XPATH, selector)
                    href = link_element.get_attribute('href')
                    if href:
                        if href.startswith('/'):
                            product_link = f"https://wilo.com{href}"
                        else:
                            product_link = href
                        break
                except:
                    continue
            
            if not product_link:
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
            self.logger.error(f"Failed to extract card data for card {index+1}: {e}")
            # Return fallback data instead of None
            return {
                'name': f"Wilo Product {index + 1}",
                'card_image_url': '',
                'product_link': '',
                'card_index': index
            }
    
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
            
            # Extract all product images and videos from carousel
            media_items = self._extract_carousel_media()
            
            # Extract product short description (left side content) - UPDATED
            short_description = self._extract_short_description_new()
            
            # Extract advantages/benefits (Ihre Vorteile) - UPDATED  
            advantages = self._extract_advantages_new()
            
            # Extract long description from the content sections - UPDATED
            long_description = self._extract_long_description_new()
            
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
            
            # DEBUG LOGGING
            self.logger.info(f"🔍 PRODUCT DEBUG for {card_data['name']}:")
            self.logger.info(f"   Short desc length: {len(short_description)} chars")
            self.logger.info(f"   Advantages count: {len(advantages)}")
            self.logger.info(f"   Long desc length: {len(long_description)} chars")
            self.logger.info(f"   Images count: {len(media_items['images'])}")
            self.logger.info(f"   Videos count: {len(media_items['videos'])}")
            
            if short_description:
                self.logger.info(f"   Short desc preview: {short_description[:100]}...")
            if advantages:
                self.logger.info(f"   First advantage: {advantages[0][:50]}...")
            
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to extract product page details: {e}")
            return None
    
    def _extract_carousel_media(self):
        """Extract all images and videos from the carousel component"""
        try:
            driver = self.browser_manager.get_driver()
            
            media_items = {
                'images': [],
                'videos': [],
                'all_media': []
            }
            
            # Extract from main carousel - UPDATED SELECTORS
            try:
                # Main carousel images
                carousel_selectors = [
                    "//div[contains(@class, 'carousel')]//img",
                    "//div[contains(@class, 'carousel-item')]//img",
                    "//div[@role='listitem']//img"
                ]
                
                for selector in carousel_selectors:
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
                
                # Thumbnail images at bottom
                thumbnail_selectors = [
                    "//div[contains(@class, 'cl-image-preview')]//img",
                    "//div[contains(@class, 'image-preview')]//img"
                ]
                
                for selector in thumbnail_selectors:
                    try:
                        thumbnails = driver.find_elements(By.XPATH, selector)
                        for thumb in thumbnails:
                            src = thumb.get_attribute('src')
                            if src and src not in media_items['images']:
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                media_items['images'].append(src)
                                media_items['all_media'].append({
                                    'type': 'thumbnail',
                                    'url': src,
                                    'alt': thumb.get_attribute('alt') or ''
                                })
                    except:
                        continue
                        
            except Exception as e:
                self.logger.debug(f"Carousel image extraction failed: {e}")
            
            # Find videos - look for video elements or video thumbnails
            try:
                video_selectors = [
                    "//video//source",
                    "//iframe[contains(@src, 'video')]",
                    "//img[contains(@src, 'still')]",  # Video thumbnails
                    "//img[contains(@src, 'video')]"
                ]
                
                for selector in video_selectors:
                    try:
                        videos = driver.find_elements(By.XPATH, selector)
                        for video in videos:
                            src = video.get_attribute('src')
                            if src and src not in media_items['videos']:
                                if src.startswith('//'):
                                    src = f"https:{src}"
                                elif src.startswith('/'):
                                    src = f"https://wilo.com{src}"
                                
                                media_items['videos'].append(src)
                                media_items['all_media'].append({
                                    'type': 'video',
                                    'url': src,
                                    'title': video.get_attribute('alt') or ''
                                })
                    except:
                        continue
                        
            except Exception as e:
                self.logger.debug(f"Video extraction failed: {e}")
            
            self.logger.info(f"Extracted {len(media_items['images'])} images and {len(media_items['videos'])} videos from carousel")
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract carousel media: {e}")
            return {'images': [], 'videos': [], 'all_media': []}
    
    def _extract_short_description_new(self):
        """Extract short description from the specific left side element"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for the specific element structure you provided
            short_desc_selectors = [
                "//div[@class='pl-md-8 col']//h3",
                "//div[@class='pl-md-8 col']//div//p",
                "//div[contains(@class, 'pl-md-8')]//h3",
                "//div[contains(@class, 'pl-md-8')]//p"
            ]
            
            short_description_parts = []
            
            for selector in short_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 10:  # Only meaningful content
                            short_description_parts.append(text)
                except:
                    continue
            
            # Combine all parts
            short_description = " ".join(short_description_parts)
            
            self.logger.info(f"Extracted short description: {len(short_description)} characters")
            return short_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract short description: {e}")
            return ""
    
    def _extract_advantages_new(self):
        """Extract advantages from the specific 'Ihre Vorteile' section"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for the specific advantages section you provided
            advantages_selectors = [
                "//div[@class='cl-your-advantages']//ul//li",
                "//div[contains(@class, 'cl-your-advantages')]//li",
                "//h3[contains(text(), 'Ihre Vorteile')]//following-sibling::div//li",
                "//div[contains(@class, 'cl-description')]//li"
            ]
            
            advantages = []
            
            for selector in advantages_selectors:
                try:
                    li_elements = driver.find_elements(By.XPATH, selector)
                    if li_elements:
                        for li in li_elements:
                            text = li.text.strip()
                            if text and len(text) > 20:  # Only substantial advantages
                                advantages.append(text)
                        break  # Stop after finding advantages in one selector
                except:
                    continue
            
            self.logger.info(f"Extracted {len(advantages)} advantages")
            return advantages
            
        except Exception as e:
            self.logger.error(f"Failed to extract advantages: {e}")
            return []
    
    def _extract_long_description_new(self):
        """Extract long description from the main content sections"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Look for content sections in the structure you provided
            long_desc_selectors = [
                "//div[contains(@class, 'text-module')]//div[contains(@class, 'text-wrapper')]//p",
                "//div[contains(@class, 'text-module')]//div[contains(@class, 'text-wrapper')]//h2",
                "//div[contains(@class, 'page-module')]//div[contains(@class, 'text-wrapper')]",
                "//div[contains(@class, 'two-cols-section')]//div[contains(@class, 'text-wrapper')]//p"
            ]
            
            long_description_parts = []
            
            for selector in long_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:  # Only substantial content
                            # Clean up the text
                            text = re.sub(r'\\s+', ' ', text)  # Normalize whitespace
                            if text not in long_description_parts:
                                long_description_parts.append(text)
                except:
                    continue
            
            # Combine parts with proper formatting
            long_description = "\\n\\n".join(long_description_parts)
            
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
                paragraphs = long_desc.split('\\n\\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            # Brand information
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender Hersteller von Pumpen und Pumpensystemen für Heizung, Kühlung, Klimatechnik, Wasserversorgung und Abwasserbehandlung.</p>")
            
            return "\\n".join(html_parts)
            
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
'''
    
    # Write the complete file
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(complete_scraper_content)
    
    print("✅ Completely rebuilt catalog scraper with correct indentation")

def main():
    """Main rebuild function"""
    print("🔧 COMPLETELY REBUILDING CATALOG SCRAPER")
    print("=" * 50)
    
    try:
        rebuild_catalog_scraper()
        
        print("\\n✅ CATALOG SCRAPER COMPLETELY REBUILT!")
        print("\\n🎯 What was fixed:")
        print("• All indentation errors resolved")
        print("• Enhanced card extraction with multiple fallback strategies")
        print("• Better error handling for all cards")
        print("• Comprehensive debug logging")
        print("• Robust product name extraction")
        
        print("\\n🚀 Now test the application:")
        print("python main.py")
        
    except Exception as e:
        print(f"❌ Error during rebuild: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())