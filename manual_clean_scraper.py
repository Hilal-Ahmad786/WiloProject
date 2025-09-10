#!/usr/bin/env python3
"""
Manually create a completely clean catalog scraper
"""

def create_manual_clean_scraper():
    """Manually write the entire catalog scraper file"""
    
    scraper_content = '''"""
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
    """Catalog scraper for Wilo products"""
    
    def __init__(self, settings):
        self.settings = settings
        self.browser_manager = BrowserManager(settings)
        self.logger = get_logger(__name__)
        self.is_running = False
        self.progress_callback = None
        self.products_callback = None
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
            
            if not self.browser_manager.setup_driver():
                raise Exception("Failed to setup browser")
                
            driver = self.browser_manager.get_driver()
            
            if self.progress_callback:
                self.progress_callback("Navigating to Wilo catalog page...")
            
            self.logger.info("Navigating to Wilo catalog page...")
            driver.get(self.catalog_url)
            time.sleep(5)
            
            self.browser_manager.take_screenshot("catalog_step1_initial_page.png")
            
            if self.progress_callback:
                self.progress_callback("Finding product cards...")
                
            all_products = self.extract_products_from_cards(max_products)
            
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
    
    def extract_products_from_cards(self, max_products):
        """Extract products from card elements - FIXED for stale elements"""
        try:
            driver = self.browser_manager.get_driver()
            wait = WebDriverWait(driver, 15)
            
            time.sleep(5)
            
            card_selectors = [
                "//div[contains(@class, 'card cl-overview h-100 rebrush')]",
                "//div[contains(@class, 'card') and contains(@class, 'cl-overview')]"
            ]
            
            all_products = []
            
            for i in range(max_products):
                if not self.is_running:
                    break
                    
                if self.progress_callback:
                    self.progress_callback(f"Processing product card {i+1}/{max_products}")
                
                try:
                    self.logger.info(f"=== PROCESSING CARD {i+1} ===")
                    
                    # RE-FIND cards each time to avoid stale element reference
                    cards = []
                    for selector in card_selectors:
                        try:
                            found_cards = wait.until(EC.presence_of_all_elements_located((By.XPATH, selector)))
                            if found_cards and len(found_cards) > i:
                                cards = found_cards
                                self.logger.info(f"Re-found {len(cards)} cards for iteration {i+1}")
                                break
                        except TimeoutException:
                            continue
                    
                    if not cards or len(cards) <= i:
                        self.logger.warning(f"No card found at position {i+1}")
                        break
                    
                    card = cards[i]  # Get the specific card for this iteration
                    
                    # Extract card data
                    card_data = self.extract_card_data_safe(card, i)
                    
                    if card_data:
                        # Click and extract details
                        product_detail = self.get_product_details_safe(card, card_data, i)
                        
                        if product_detail:
                            all_products.append(product_detail)
                            
                            if self.products_callback:
                                self.products_callback(product_detail)
                            
                            self.logger.info(f"✅ Successfully extracted: {product_detail['name']}")
                        else:
                            self.logger.warning(f"❌ Failed to get details for card {i+1}")
                    else:
                        self.logger.warning(f"❌ Failed to extract card data for card {i+1}")
                    
                    time.sleep(2)
                    
                except Exception as e:
                    self.logger.error(f"❌ Error processing card {i+1}: {e}")
                    continue
            
            self.logger.info(f"=== EXTRACTION COMPLETE ===")
            self.logger.info(f"Successfully processed {len(all_products)} out of {max_products} cards")
            
            return all_products
            
        except Exception as e:
            self.logger.error(f"Failed to extract products from cards: {e}")
            return []
    
    def extract_card_data_safe(self, card, index):
        """Extract basic data from card - SAFE version"""
        try:
            product_name = f"Product {index + 1}"
            
            image_url = ""
            try:
                img_element = card.find_element(By.XPATH, ".//img")
                img_src = img_element.get_attribute('src')
                if img_src:
                    if img_src.startswith('//'):
                        image_url = f"https:{img_src}"
                    elif img_src.startswith('/'):
                        image_url = f"https://wilo.com{img_src}"
                    else:
                        image_url = img_src
            except:
                self.logger.debug(f"Could not find image in card {index+1}")
            
            product_link = ""
            link_selectors = [
                ".//a[@class='stretched-link']",
                ".//a[contains(@class, 'stretched')]",
                ".//a[@href]"
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
            
            card_data = {
                'name': product_name,
                'card_image_url': image_url,
                'product_link': product_link,
                'card_index': index
            }
            
            self.logger.info(f"Extracted card data for position {index+1}")
            return card_data
            
        except Exception as e:
            self.logger.error(f"Failed to extract card data: {e}")
            return {
                'name': f"Product {index + 1}",
                'card_image_url': '',
                'product_link': '',
                'card_index': index
            }
    
    def get_product_details_safe(self, card, card_data, index):
        """Click on card and extract product details - SAFE version"""
        try:
            driver = self.browser_manager.get_driver()
            
            # Try clicking via link first
            clicked = False
            if card_data.get('product_link'):
                try:
                    link_element = card.find_element(By.XPATH, ".//a[@class='stretched-link']")
                    driver.execute_script("arguments[0].click();", link_element)
                    self.logger.info(f"Clicked via link for card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.warning(f"Link click failed: {e}")
            
            # If link click failed, try clicking the card itself
            if not clicked:
                try:
                    driver.execute_script("arguments[0].click();", card)
                    self.logger.info(f"Clicked directly on card {index+1}")
                    clicked = True
                except Exception as e:
                    self.logger.error(f"Direct card click failed: {e}")
            
            if not clicked:
                self.logger.error(f"Could not click card {index+1}")
                return None
            
            time.sleep(5)
            self.browser_manager.take_screenshot(f"catalog_product_{index}_page.png")
            
            product_details = self.extract_product_page_details(card_data)
            
            driver.back()
            time.sleep(3)
            
            return product_details
            
        except Exception as e:
            self.logger.error(f"Failed to get product details: {e}")
            return None
    
    def extract_product_page_details(self, card_data):
        """Extract detailed info from product page"""
        try:
            driver = self.browser_manager.get_driver()
            
            real_product_name = ""
            try:
                h1_element = driver.find_element(By.XPATH, "//h1[@class='m-0']")
                real_product_name = h1_element.text.strip()
                self.logger.info(f"Extracted real name from H1: {real_product_name}")
            except:
                try:
                    h1_element = driver.find_element(By.XPATH, "//h1")
                    real_product_name = h1_element.text.strip()
                    self.logger.info(f"Extracted name from fallback H1: {real_product_name}")
                except:
                    real_product_name = f"Wilo Product {card_data.get('card_index', 0) + 1}"
                    self.logger.warning(f"Using fallback name: {real_product_name}")
            
            media_items = self.extract_carousel_media()
            short_description = self.extract_short_description()
            advantages = self.extract_advantages()
            long_description = self.extract_long_description()
            
            product = {
                'id': f"catalog_{card_data['card_index']+1}_{int(time.time())}",
                'name': real_product_name,
                'category': 'Industrie Heizung',
                'subcategory': 'Heizungspumpen',
                'source': 'catalog',
                'card_image_url': card_data['card_image_url'],
                'product_images': media_items['images'],
                'product_videos': media_items['videos'],
                'all_media': media_items['all_media'],
                'short_description': short_description,
                'advantages': advantages,
                'long_description': long_description,
                'full_description': self.build_full_description(short_description, advantages, long_description),
                'product_url': driver.current_url,
                'extracted_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                'specifications': {
                    'brand': 'Wilo',
                    'series': real_product_name,
                    'application': 'Industrie Heizung',
                    'type': 'Heizungspumpe'
                },
                'price': 'Price on request',
                'currency': 'EUR',
                'country': 'Germany',
                'status': 'Catalog Product - Real Extraction'
            }
            
            self.logger.info(f"🔍 PRODUCT DEBUG for {real_product_name}:")
            self.logger.info(f"   Real name from H1: {real_product_name}")
            self.logger.info(f"   Short desc length: {len(short_description)} chars")
            self.logger.info(f"   Advantages count: {len(advantages)}")
            self.logger.info(f"   Product images: {len(media_items['images'])}")
            
            if short_description:
                self.logger.info(f"   Short desc preview: {short_description[:100]}...")
            if advantages:
                self.logger.info(f"   First advantage: {advantages[0][:50]}...")
            
            return product
            
        except Exception as e:
            self.logger.error(f"Failed to extract product details: {e}")
            return None
    
    def extract_carousel_media(self):
        """Extract images and videos from carousel"""
        try:
            driver = self.browser_manager.get_driver()
            
            media_items = {
                'images': [],
                'videos': [],
                'all_media': []
            }
            
            try:
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
                self.logger.debug(f"Carousel extraction failed: {e}")
            
            try:
                video_selectors = [
                    "//video//source",
                    "//iframe[contains(@src, 'video')]"
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
            
            self.logger.info(f"Extracted {len(media_items['images'])} images and {len(media_items['videos'])} videos")
            return media_items
            
        except Exception as e:
            self.logger.error(f"Failed to extract media: {e}")
            return {'images': [], 'videos': [], 'all_media': []}
    
    def extract_short_description(self):
        """Extract short description"""
        try:
            driver = self.browser_manager.get_driver()
            
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
                        if text and len(text) > 10:
                            short_description_parts.append(text)
                except:
                    continue
            
            short_description = " ".join(short_description_parts)
            self.logger.info(f"Extracted short description: {len(short_description)} characters")
            return short_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract short description: {e}")
            return ""
    
    def extract_advantages(self):
        """Extract advantages list"""
        try:
            driver = self.browser_manager.get_driver()
            
            advantages_selectors = [
                "//div[@class='cl-your-advantages']//ul//li",
                "//div[contains(@class, 'cl-your-advantages')]//li",
                "//h3[contains(text(), 'Ihre Vorteile')]//following-sibling::div//li"
            ]
            
            advantages = []
            
            for selector in advantages_selectors:
                try:
                    li_elements = driver.find_elements(By.XPATH, selector)
                    if li_elements:
                        for li in li_elements:
                            text = li.text.strip()
                            if text and len(text) > 20:
                                advantages.append(text)
                        break
                except:
                    continue
            
            self.logger.info(f"Extracted {len(advantages)} advantages")
            return advantages
            
        except Exception as e:
            self.logger.error(f"Failed to extract advantages: {e}")
            return []
    
    def extract_long_description(self):
        """Extract long description"""
        try:
            driver = self.browser_manager.get_driver()
            
            long_desc_selectors = [
                "//div[contains(@class, 'text-module')]//div[contains(@class, 'text-wrapper')]//p",
                "//div[contains(@class, 'page-module')]//div[contains(@class, 'text-wrapper')]"
            ]
            
            long_description_parts = []
            
            for selector in long_desc_selectors:
                try:
                    elements = driver.find_elements(By.XPATH, selector)
                    for elem in elements:
                        text = elem.text.strip()
                        if text and len(text) > 50:
                            text = re.sub(r'\\s+', ' ', text)
                            if text not in long_description_parts:
                                long_description_parts.append(text)
                except:
                    continue
            
            long_description = "\\n\\n".join(long_description_parts)
            self.logger.info(f"Extracted long description: {len(long_description)} characters")
            return long_description
            
        except Exception as e:
            self.logger.error(f"Failed to extract long description: {e}")
            return ""
    
    def build_full_description(self, short_desc, advantages, long_desc):
        """Build comprehensive description"""
        try:
            html_parts = []
            
            if short_desc:
                html_parts.append(f"<div class='product-intro'>{short_desc}</div>")
            
            if advantages:
                html_parts.append("<h3>Ihre Vorteile</h3>")
                html_parts.append("<ul>")
                for advantage in advantages:
                    html_parts.append(f"<li>{advantage}</li>")
                html_parts.append("</ul>")
            
            if long_desc:
                paragraphs = long_desc.split('\\n\\n')
                for paragraph in paragraphs:
                    if paragraph.strip():
                        html_parts.append(f"<p>{paragraph.strip()}</p>")
            
            html_parts.append("<h3>Über Wilo</h3>")
            html_parts.append("<p>Wilo ist ein führender Hersteller von Pumpen und Pumpensystemen.</p>")
            
            return "\\n".join(html_parts)
            
        except Exception as e:
            self.logger.error(f"Failed to build description: {e}")
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
            
            if "wilo.com" in driver.current_url and "katalog" in driver.current_url.lower():
                self.logger.info("Navigation test successful")
                if self.progress_callback:
                    self.progress_callback("Navigation test successful!", stop_progress=True)
                return True
            else:
                self.logger.error("Navigation test failed")
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
        self.logger.info("Stopping catalog scraper...")
        self.is_running = False
        if self.progress_callback:
            self.progress_callback("Catalog scraping stopped", stop_progress=True)
'''
    
    with open('scraper/wilo_catalog_scraper.py', 'w') as f:
        f.write(scraper_content)
    
    print("✅ Created manual clean catalog scraper")

def main():
    """Main function"""
    print("🔧 CREATING MANUAL CLEAN CATALOG SCRAPER")
    print("=" * 45)
    
    try:
        create_manual_clean_scraper()
        
        print("\\n✅ MANUAL CLEAN SCRAPER CREATED!")
        print("\\n🎯 Features:")
        print("• Perfect indentation (written manually)")
        print("• Fixes stale element references")
        print("• H1 title extraction")
        print("• Real content extraction")
        print("• Works with both cards")
        
        print("\\n🚀 Now test:")
        print("python main.py")
        
        print("\\n📋 Expected:")
        print("• Both cards should process successfully")
        print("• Real H1 titles extracted")
        print("• Ready for Shopify upload fix")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())